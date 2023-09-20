from render_stocks import render_stock_on_matrix
import time

def main():
    while True:
        render_stock_on_matrix('AAPL')
        time.sleep(600)  # Update every 10 minutes

if __name__ == "__main__":
    main()

