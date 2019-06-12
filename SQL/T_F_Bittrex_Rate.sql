/*
Navicat SQL Server Data Transfer

Source Server         : BI_DWH
Source Server Version : 105000
Source Host           : 127.0.0.1:1433
Source Database       : LidyaRichDWH
Source Schema         : IB_RPA

Target Server Type    : SQL Server
Target Server Version : 105000
File Encoding         : 65001

Date: 2019-06-11 11:08:22
*/


-- ----------------------------
-- Table structure for T_F_Bittrex_Rate
-- ----------------------------
DROP TABLE [IB_RPA].[T_F_Bittrex_Rate]
GO
CREATE TABLE [IB_RPA].[T_F_Bittrex_Rate] (
[Id] int NOT NULL IDENTITY(1,1) ,
[Vendor] varchar(15) NULL ,
[Pair] varchar(10) NULL ,
[AskRate] decimal(32,10) NULL ,
[BidRate] decimal(32,10) NULL ,
[24hVolume] decimal(32,10) NULL ,
[HighPrice] decimal(32,10) NULL ,
[LowPrice] decimal(32,10) NULL ,
[Time] datetime NULL ,
[CreateDate] datetime NULL ,
[CreateUser] varchar(10) NULL 
)


GO
DBCC CHECKIDENT(N'[IB_RPA].[T_F_Bittrex_Rate]', RESEED, 3936)
GO

-- ----------------------------
-- Indexes structure for table T_F_Bittrex_Rate
-- ----------------------------
CREATE INDEX [Createdate] ON [IB_RPA].[T_F_Bittrex_Rate]
([CreateDate] ASC) 
GO
CREATE INDEX [ID] ON [IB_RPA].[T_F_Bittrex_Rate]
([Id] ASC) 
GO

-- ----------------------------
-- Primary Key structure for table T_F_Bittrex_Rate
-- ----------------------------
ALTER TABLE [IB_RPA].[T_F_Bittrex_Rate] ADD PRIMARY KEY ([Id])
GO
