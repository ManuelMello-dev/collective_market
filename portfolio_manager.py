import logging
import threading
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Individual position in a security"""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime = field(default_factory=datetime.now)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized profit/loss"""
        return self.quantity * (current_price - self.entry_price)
    
    def pnl_pct(self, current_price: float) -> float:
        """Calculate P&L percentage"""
        return ((current_price - self.entry_price) / self.entry_price) * 100
    
    def check_stop_loss(self, current_price: float) -> bool:
        """Check if stop loss is triggered"""
        if self.stop_loss and current_price <= self.stop_loss:
            return True
        return False
    
    def check_take_profit(self, current_price: float) -> bool:
        """Check if take profit is triggered"""
        if self.take_profit and current_price >= self.take_profit:
            return True
        return False


class PortfolioManager:
    """Production-grade portfolio management with risk controls"""
    
    def __init__(
        self,
        initial_capital: float = 100000,
        max_position_size: float = 0.1,  # 10% max per position
        max_total_exposure: float = 0.8,  # 80% max deployed
        stop_loss_pct: float = 0.05,      # 5% stop loss
        take_profit_pct: float = 0.15,    # 15% take profit
        max_daily_loss: float = 0.03,     # 3% max daily drawdown
    ):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.max_position_size = max_position_size
        self.max_total_exposure = max_total_exposure
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_daily_loss = max_daily_loss
        
        self.positions: Dict[str, Position] = {}
        self.closed_pnl = 0.0
        self.daily_pnl = 0.0
        self.daily_start_capital = initial_capital
        self.trade_count = 0
        self.win_count = 0
        self.loss_count = 0
        
        # Metrics
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 0.0,
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        # History for analytics
        self.pnl_history = []
        self.equity_curve = [initial_capital]
        
        logger.info(f"Portfolio initialized with ${initial_capital:,.2f}")
    
    def _calculate_position_size(self, current_price: float) -> int:
        """Calculate position size based on risk parameters"""
        max_position_value = self.initial_capital * self.max_position_size
        quantity = int(max_position_value / current_price)
        return max(1, quantity)
    
    def _check_risk_limits(self) -> bool:
        """Check if we're within risk limits"""
        # Check daily loss limit
        daily_loss_pct = (self.daily_pnl / self.daily_start_capital)
        if daily_loss_pct < -self.max_daily_loss:
            logger.warning(f"Daily loss limit hit: {daily_loss_pct:.2%}")
            return False
        
        # Check total exposure
        total_exposure = sum(
            pos.quantity * pos.entry_price 
            for pos in self.positions.values()
        )
        exposure_pct = total_exposure / self.initial_capital
        if exposure_pct > self.max_total_exposure:
            logger.warning(f"Max exposure limit hit: {exposure_pct:.2%}")
            return False
        
        return True
    
    def process_signal(
        self, 
        symbol: str, 
        signal: str, 
        current_price: float,
        timestamp: Optional[datetime] = None
    ) -> Optional[str]:
        """Process trading signal with risk management
        
        Returns:
            Action taken: 'BUY', 'SELL', 'STOP_LOSS', 'TAKE_PROFIT', or None
        """
        with self.lock:
            timestamp = timestamp or datetime.now()
            
            # Check existing positions for exit conditions
            if symbol in self.positions:
                pos = self.positions[symbol]
                
                # Check stop loss
                if pos.check_stop_loss(current_price):
                    self._close_position(symbol, current_price, 'STOP_LOSS')
                    return 'STOP_LOSS'
                
                # Check take profit
                if pos.check_take_profit(current_price):
                    self._close_position(symbol, current_price, 'TAKE_PROFIT')
                    return 'TAKE_PROFIT'
            
            # Process new signals
            if signal == 'BUY':
                return self._open_position(symbol, current_price, timestamp)
            elif signal == 'SELL':
                return self._close_position(symbol, current_price, 'SIGNAL')
            
            return None
    
    def _open_position(
        self, 
        symbol: str, 
        current_price: float,
        timestamp: datetime
    ) -> Optional[str]:
        """Open new position with risk controls"""
        # Don't open if already holding
        if symbol in self.positions:
            return None
        
        # Check risk limits
        if not self._check_risk_limits():
            return None
        
        # Calculate position size
        quantity = self._calculate_position_size(current_price)
        cost = quantity * current_price
        
        # Check sufficient capital
        if cost > self.capital:
            logger.debug(f"Insufficient capital for {symbol}: need ${cost:.2f}, have ${self.capital:.2f}")
            return None
        
        # Calculate stop loss and take profit levels
        stop_loss = current_price * (1 - self.stop_loss_pct)
        take_profit = current_price * (1 + self.take_profit_pct)
        
        # Create position
        position = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=current_price,
            entry_time=timestamp,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        self.positions[symbol] = position
        self.capital -= cost
        self.trade_count += 1
        self.metrics['total_trades'] += 1
        
        logger.info(
            f"OPEN {symbol}: {quantity} @ ${current_price:.2f} "
            f"| SL: ${stop_loss:.2f} | TP: ${take_profit:.2f} "
            f"| Capital remaining: ${self.capital:.2f}"
        )
        
        return 'BUY'
    
    def _close_position(
        self, 
        symbol: str, 
        current_price: float,
        reason: str = 'SIGNAL'
    ) -> Optional[str]:
        """Close existing position"""
        if symbol not in self.positions:
            return None
        
        position = self.positions.pop(symbol)
        proceeds = position.quantity * current_price
        pnl = position.unrealized_pnl(current_price)
        pnl_pct = position.pnl_pct(current_price)
        
        self.capital += proceeds
        self.closed_pnl += pnl
        self.daily_pnl += pnl
        self.metrics['total_pnl'] = self.closed_pnl
        
        # Update win/loss stats
        if pnl > 0:
            self.win_count += 1
            self.metrics['winning_trades'] += 1
        else:
            self.loss_count += 1
            self.metrics['losing_trades'] += 1
        
        self.metrics['win_rate'] = (
            self.win_count / self.trade_count if self.trade_count > 0 else 0
        )
        
        # Update equity curve
        total_value = self.get_total_value({symbol: current_price})
        self.equity_curve.append(total_value)
        self.pnl_history.append(pnl)
        
        logger.info(
            f"CLOSE {symbol} ({reason}): {position.quantity} @ ${current_price:.2f} "
            f"| P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%) "
            f"| Total P&L: ${self.closed_pnl:+,.2f}"
        )
        
        return 'SELL'
    
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value including unrealized P&L"""
        unrealized_pnl = sum(
            pos.unrealized_pnl(current_prices.get(pos.symbol, pos.entry_price))
            for pos in self.positions.values()
        )
        return self.capital + unrealized_pnl
    
    def get_unrealized_pnl(self, current_prices: Dict[str, float]) -> float:
        """Get total unrealized P&L"""
        return sum(
            pos.unrealized_pnl(current_prices.get(pos.symbol, pos.entry_price))
            for pos in self.positions.values()
        )
    
    def get_portfolio_state(self, current_prices: Dict[str, float]) -> dict:
        """Get comprehensive portfolio state"""
        unrealized_pnl = self.get_unrealized_pnl(current_prices)
        total_value = self.get_total_value(current_prices)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'capital': self.capital,
            'positions_count': len(self.positions),
            'positions': {
                sym: {
                    'quantity': pos.quantity,
                    'entry_price': pos.entry_price,
                    'current_price': current_prices.get(sym, pos.entry_price),
                    'unrealized_pnl': pos.unrealized_pnl(current_prices.get(sym, pos.entry_price)),
                    'pnl_pct': pos.pnl_pct(current_prices.get(sym, pos.entry_price)),
                }
                for sym, pos in self.positions.items()
            },
            'closed_pnl': self.closed_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': self.closed_pnl + unrealized_pnl,
            'total_value': total_value,
            'return_pct': ((total_value - self.initial_capital) / self.initial_capital) * 100,
            'metrics': self.metrics,
        }
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio from P&L history"""
        if len(self.pnl_history) < 2:
            return 0.0
        
        returns = np.array(self.pnl_history) / self.initial_capital
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
        self.metrics['sharpe_ratio'] = sharpe
        return sharpe
    
    def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve"""
        if len(self.equity_curve) < 2:
            return 0.0
        
        equity = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        max_dd = drawdown.min()
        
        self.metrics['max_drawdown'] = max_dd
        return max_dd
    
    def reset_daily_metrics(self):
        """Reset daily tracking metrics (call at start of each trading day)"""
        with self.lock:
            self.daily_pnl = 0.0
            self.daily_start_capital = self.capital
            logger.info("Daily metrics reset")
    
    def get_performance_summary(self, current_prices: Dict[str, float]) -> dict:
        """Get comprehensive performance summary"""
        state = self.get_portfolio_state(current_prices)
        sharpe = self.calculate_sharpe_ratio()
        max_dd = self.calculate_max_drawdown()
        
        return {
            **state,
            'performance': {
                'sharpe_ratio': sharpe,
                'max_drawdown': max_dd,
                'win_rate': self.metrics['win_rate'],
                'total_trades': self.metrics['total_trades'],
                'avg_win': (
                    sum(p for p in self.pnl_history if p > 0) / self.win_count
                    if self.win_count > 0 else 0
                ),
                'avg_loss': (
                    sum(p for p in self.pnl_history if p < 0) / self.loss_count
                    if self.loss_count > 0 else 0
                ),
            }
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create portfolio
    portfolio = PortfolioManager(
        initial_capital=100000,
        max_position_size=0.1,
        stop_loss_pct=0.05,
        take_profit_pct=0.15
    )
    
    # Simulate some trades
    current_prices = {}
    
    # Buy signals
    portfolio.process_signal('AAPL', 'BUY', 150.0)
    current_prices['AAPL'] = 150.0
    
    portfolio.process_signal('MSFT', 'BUY', 300.0)
    current_prices['MSFT'] = 300.0
    
    # Price moves
    current_prices['AAPL'] = 157.5  # +5%
    current_prices['MSFT'] = 285.0  # -5%
    
    # Check portfolio
    state = portfolio.get_portfolio_state(current_prices)
    print(f"\nPortfolio State:")
    print(f"Total Value: ${state['total_value']:,.2f}")
    print(f"Total P&L: ${state['total_pnl']:+,.2f} ({state['return_pct']:+.2f}%)")
    print(f"Positions: {state['positions_count']}")
    
    # Trigger take profit on AAPL
    current_prices['AAPL'] = 175.0  # +16.7% - above take profit
    portfolio.process_signal('AAPL', 'HOLD', 175.0)
    
    # Get performance summary
    summary = portfolio.get_performance_summary(current_prices)
    print(f"\nPerformance Summary:")
    print(f"Win Rate: {summary['performance']['win_rate']:.1%}")
    print(f"Total Trades: {summary['performance']['total_trades']}")
