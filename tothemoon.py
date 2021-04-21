#!/usr/bin/python
import requests
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Get crypto prices using coincap api')
parser.add_argument('-s', '--symbols', nargs='+', help='Filter by symbol')
parser.add_argument('-n', '--number', type=int, help='Number of top results to display', default=10)
parser.add_argument('-N', '--notify', help="Send notifications instead of printing to sdtout", action="store_true")

args = parser.parse_args()

data = requests.get('http://api.coincap.io/v2/assets').json()

symbols = []

if(args.symbols):
    symbols = [x.lower() for x in args.symbols]

for index, crypto in enumerate(data['data']):
    if(not(args.symbols) and index >= args.number):
        break
    
    try:
        if((crypto['symbol'].lower() in symbols or not(args.symbols))):
            if(args.notify):
                subprocess.Popen(['notify-send', f"{crypto['symbol']}", f"{float(crypto['priceUsd']):.5g} USD ({float(crypto['changePercent24Hr']):.2f})%"])
            else:
                print(f"{crypto['symbol']} {float(crypto['priceUsd']):.5g} USD ({float(crypto['changePercent24Hr']):.2f})%")       
    except TypeError:
        pass
