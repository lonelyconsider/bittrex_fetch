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

Date: 2019-06-11 11:08:16
*/


-- ----------------------------
-- Table structure for T_F_Bittrex_Order
-- ----------------------------
DROP TABLE [IB_RPA].[T_F_Bittrex_Order]
GO
CREATE TABLE [IB_RPA].[T_F_Bittrex_Order] (
[Id] int NOT NULL IDENTITY(1,1) ,
[Vendor] varchar(30) NULL ,
[Pair] varchar(10) NULL ,
[Type] varchar(20) NULL ,
[Price] decimal(32,8) NULL ,
[Quantity] decimal(32,8) NULL ,
[No.] int NULL ,
[CreateDate] datetime NULL ,
[CreateUser] varchar(10) NULL 
)


GO
DBCC CHECKIDENT(N'[IB_RPA].[T_F_Bittrex_Order]', RESEED, 763452)
GO
