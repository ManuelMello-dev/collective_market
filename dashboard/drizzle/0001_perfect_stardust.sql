CREATE TABLE `alert_rules` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(255) NOT NULL,
	`type` enum('circuit_breaker','drawdown','error_rate','latency') NOT NULL,
	`threshold` decimal(10,4) NOT NULL,
	`isActive` boolean DEFAULT true,
	`metadata` json,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `alert_rules_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `market_data` (
	`id` int AUTO_INCREMENT NOT NULL,
	`symbol` varchar(50) NOT NULL,
	`price` decimal(20,8) NOT NULL,
	`volume` decimal(20,2) NOT NULL,
	`sentiment` decimal(5,4),
	`source` varchar(50) NOT NULL,
	`recordedAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `market_data_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `microservices_health` (
	`id` int AUTO_INCREMENT NOT NULL,
	`service` varchar(100) NOT NULL,
	`isHealthy` boolean NOT NULL,
	`latencyMs` decimal(10,2),
	`errorCount` int DEFAULT 0,
	`lastError` text,
	`checkedAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `microservices_health_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `portfolio_positions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`symbol` varchar(50) NOT NULL,
	`quantity` decimal(20,8) NOT NULL,
	`entryPrice` decimal(20,8) NOT NULL,
	`currentPrice` decimal(20,8) NOT NULL,
	`stopLoss` decimal(20,8),
	`takeProfit` decimal(20,8),
	`unrealizedPnl` decimal(20,2) NOT NULL,
	`pnlPercent` decimal(10,4) NOT NULL,
	`openedAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `portfolio_positions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `portfolio_snapshots` (
	`id` int AUTO_INCREMENT NOT NULL,
	`totalValue` decimal(20,2) NOT NULL,
	`capital` decimal(20,2) NOT NULL,
	`closedPnl` decimal(20,2) NOT NULL,
	`unrealizedPnl` decimal(20,2) NOT NULL,
	`positionsCount` int NOT NULL,
	`sharpeRatio` decimal(10,4),
	`maxDrawdown` decimal(10,4),
	`winRate` decimal(5,4),
	`snapshotAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `portfolio_snapshots_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `replay_sessions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(255) NOT NULL,
	`startDate` timestamp NOT NULL,
	`endDate` timestamp NOT NULL,
	`symbols` json,
	`initialCapital` decimal(20,2) NOT NULL,
	`status` enum('pending','running','completed','failed') DEFAULT 'pending',
	`results` json,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`completedAt` timestamp,
	CONSTRAINT `replay_sessions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `simulation_states` (
	`id` int AUTO_INCREMENT NOT NULL,
	`step` int NOT NULL,
	`globalState` decimal(20,8) NOT NULL,
	`activeSignals` int NOT NULL,
	`agentPrices` json,
	`recordedAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `simulation_states_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `trading_signals` (
	`id` int AUTO_INCREMENT NOT NULL,
	`symbol` varchar(50) NOT NULL,
	`signal` enum('BUY','SELL','HOLD') NOT NULL,
	`confidence` decimal(5,4) NOT NULL,
	`price` decimal(20,8) NOT NULL,
	`reason` text,
	`executedAt` timestamp,
	`generatedAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `trading_signals_id` PRIMARY KEY(`id`)
);
