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

Date: 2019-06-11 11:08:02
*/


-- ----------------------------
-- Table structure for T_E_Bittrex_Order_Analysis
-- ----------------------------
DROP TABLE [IB_RPA].[T_E_Bittrex_Order_Analysis]
GO
CREATE TABLE [IB_RPA].[T_E_Bittrex_Order_Analysis] (
[Id] bigint NOT NULL IDENTITY(1,1) ,
[Vendor] varchar(30) NULL ,
[Pair] varchar(10) NULL ,
[IndependentVar] varchar(20) NULL ,
[AskLimit] int NULL ,
[BidLimit] int NULL ,
[AskDepth] decimal(32,8) NULL ,
[BidDepth] decimal(32,8) NULL ,
[AskSpan] decimal(10,3) NULL ,
[BidSpan] decimal(10,3) NULL ,
[CreateDate] datetime NULL ,
[HighestAsk] decimal(32,8) NULL ,
[HighestBid] decimal(32,8) NULL ,
[LowestAsk] decimal(32,8) NULL ,
[LowestBid] decimal(32,8) NULL 
)


GO
DBCC CHECKIDENT(N'[IB_RPA].[T_E_Bittrex_Order_Analysis]', RESEED, 39360)
GO
