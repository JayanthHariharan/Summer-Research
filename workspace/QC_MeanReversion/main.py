from AlgorithmImports import *

class BasicMeanReversionAlgorithm(QCAlgorithm):

    def Initialize(self):
        # 1) Back-test window & capitalcd
        self.SetStartDate(2010, 1, 1)
        self.SetEndDate(2025, 1, 1)
        self.SetCash(100_000)
        self.entry = float(self.GetParameter("Z_ENTRY", 1.0))  # Default to 2.0 if not set

        # 2) Add the security (minute-resolution for extra data points)
        self.symbol = self.add_equity("SPY", Resolution.Daily).Symbol

        # 3) Rolling window for price history
        self.period = 20
        self.window = RollingWindow[float](self.period)

        # 4) Prime the window with historical prices
        history = self.History(self.symbol, self.period, Resolution.Daily)
        for bar in history.itertuples():
            self.window.Add(float(bar.close))

    def OnData(self, data: Slice):
        bar = data.Bars.get(self.symbol)   # safer accessor
        if bar is None:
            return                         # nothing to do this minute

        price = float(bar.Close) 

        # Wait until the rolling window is full
        if not self.window.IsReady:
            return

        # Compute mean and standard deviation
        values    = list(self.window)
        mean      = sum(values) / self.period
        variance  = sum((x - mean) ** 2 for x in values) / self.period
        std       = variance ** 0.5

        # 5) Trading logic: long when price < mean − std, exit when > mean + std
        if price < mean - (self.entry * std):
            self.SetHoldings(self.symbol, 1.0)        # 100 % long
        elif price > mean + (self.entry * std):
            self.Liquidate(self.symbol)

    def OnEndOfDay(self):
        # Plot only after warm-up
        if self.window.IsReady:
            mean = sum(self.window) / self.period
            self.Plot("Data", "Price", self.Securities[self.symbol].Price)
            self.Plot("Data", "Mean",  mean)