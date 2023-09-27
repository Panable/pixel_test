import time
from render_stocks2 import render_stock_on_matrix

if __name__ == "__main__":
    try:
        while True:
            # Display the stock data for AAPL
            render_stock_on_matrix('AAPL')
            
            # Wait for a minute before refreshing. 
            # This delay ensures you aren't hitting the API too frequently. Adjust as needed.
            time.sleep(600)

    except KeyboardInterrupt:
        # Cleanup actions can be placed here if needed
        pass

