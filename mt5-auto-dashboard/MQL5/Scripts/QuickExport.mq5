//+------------------------------------------------------------------+
//| QuickExport.mq5                                                 |
//| One-click manual export script                                  |
//+------------------------------------------------------------------+

#property script_show_inputs
#property copyright "Quick Export Script"
#property version   "1.00"
#property description "One-click manual data export"

input string   EAName = "ManualExport";
input string   ExportPath = "MT5_Data/";
input bool     ExportAccount = true;
input bool     ExportPositions = true;
input bool     ExportHistory = true;

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   string timestamp = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS);
   StringReplace(timestamp, ":", "-");
   
   Print("=== Starting Quick Export ===");
   
   if(ExportAccount)
   {
      string accountFile = ExportPath + EAName + "_Account_" + timestamp + ".csv";
      ExportAccountInfo(accountFile);
   }
   
   if(ExportPositions)
   {
      string positionsFile = ExportPath + EAName + "_Positions_" + timestamp + ".csv";
      ExportCurrentPositions(positionsFile);
   }
   
   if(ExportHistory)
   {
      string historyFile = ExportPath + EAName + "_History_" + timestamp + ".csv";
      ExportTradeHistory(historyFile);
   }
   
   Print("=== Quick Export Completed ===");
}

//+------------------------------------------------------------------+
//| Export Account Information                                      |
//+------------------------------------------------------------------+
void ExportAccountInfo(string filename)
{
   int file_handle = FileOpen(filename, FILE_WRITE|FILE_CSV|FILE_ANSI, ";");
   
   if(file_handle == INVALID_HANDLE)
   {
      Print("Error creating account file: ", filename);
      return;
   }
   
   FileWrite(file_handle, "EA_Name;Timestamp;Balance;Equity;Margin;FreeMargin;MarginLevel;Profit;Currency;Server");
   
   string data = StringFormat("%s;%s;%.2f;%.2f;%.2f;%.2f;%.2f;%.2f;%s;%s",
      EAName,
      TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS),
      AccountInfoDouble(ACCOUNT_BALANCE),
      AccountInfoDouble(ACCOUNT_EQUITY),
      AccountInfoDouble(ACCOUNT_MARGIN),
      AccountInfoDouble(ACCOUNT_MARGIN_FREE),
      AccountInfoDouble(ACCOUNT_MARGIN_LEVEL),
      AccountInfoDouble(ACCOUNT_PROFIT),
      AccountInfoString(ACCOUNT_CURRENCY),
      AccountInfoString(ACCOUNT_SERVER)
   );
   
   FileWrite(file_handle, data);
   FileClose(file_handle);
   Print("Account info exported: ", filename);
}

//+------------------------------------------------------------------+
//| Export Current Positions                                        |
//+------------------------------------------------------------------+
void ExportCurrentPositions(string filename)
{
   int file_handle = FileOpen(filename, FILE_WRITE|FILE_CSV|FILE_ANSI, ";");
   
   if(file_handle == INVALID_HANDLE)
   {
      Print("Error creating positions file: ", filename);
      return;
   }
   
   FileWrite(file_handle, "EA_Name;Timestamp;Ticket;Symbol;Type;Volume;OpenPrice;CurrentPrice;Profit;Swap;Commission;OpenTime");
   
   int totalPositions = (int)PositionsTotal();
   string currentTime = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS);
   
   for(int i = 0; i < totalPositions; i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         string data = StringFormat("%s;%s;%I64d;%s;%d;%.2f;%.5f;%.5f;%.2f;%.2f;%.2f;%s",
            EAName,
            currentTime,
            ticket,
            PositionGetString(POSITION_SYMBOL),
            PositionGetInteger(POSITION_TYPE),
            PositionGetDouble(POSITION_VOLUME),
            PositionGetDouble(POSITION_PRICE_OPEN),
            PositionGetDouble(POSITION_PRICE_CURRENT),
            PositionGetDouble(POSITION_PROFIT),
            PositionGetDouble(POSITION_SWAP),
            PositionGetDouble(POSITION_COMMISSION),
            TimeToString((datetime)PositionGetInteger(POSITION_TIME))
         );
         
         FileWrite(file_handle, data);
      }
   }
   
   FileClose(file_handle);
   Print("Positions exported: ", filename, " - Count: ", totalPositions);
}

//+------------------------------------------------------------------+
//| Export Trade History                                            |
//+------------------------------------------------------------------+
void ExportTradeHistory(string filename)
{
   int file_handle = FileOpen(filename, FILE_WRITE|FILE_CSV|FILE_ANSI, ";");
   
   if(file_handle == INVALID_HANDLE)
   {
      Print("Error creating history file: ", filename);
      return;
   }
   
   FileWrite(file_handle, "EA_Name;Time;Deal;Type;Symbol;Volume;Price;Profit;Commission;Comment");
   
   datetime start_time = 0;
   datetime end_time = TimeCurrent();
   
   if(HistorySelect(start_time, end_time))
   {
      int total_deals = (int)HistoryDealsTotal();
      for(int i = 0; i < total_deals; i++)
      {
         ulong deal_ticket = HistoryDealGetTicket(i);
         if(deal_ticket > 0)
         {
            string data = StringFormat("%s;%s;%I64d;%d;%s;%.2f;%.5f;%.2f;%.2f;%s",
               EAName,
               TimeToString((datetime)HistoryDealGetInteger(deal_ticket, DEAL_TIME)),
               deal_ticket,
               HistoryDealGetInteger(deal_ticket, DEAL_TYPE),
               HistoryDealGetString(deal_ticket, DEAL_SYMBOL),
               HistoryDealGetDouble(deal_ticket, DEAL_VOLUME),
               HistoryDealGetDouble(deal_ticket, DEAL_PRICE),
               HistoryDealGetDouble(deal_ticket, DEAL_PROFIT),
               HistoryDealGetDouble(deal_ticket, DEAL_COMMISSION),
               HistoryDealGetString(deal_ticket, DEAL_COMMENT)
            );
            
            FileWrite(file_handle, data);
         }
      }
   }
   
   FileClose(file_handle);
   Print("Trade history exported: ", filename);
}