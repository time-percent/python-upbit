A python3 wrapper for UPBit

# install

```bash
pip3 install python-upbit
```

# Usage 

```python
from upbit import UPBitClient

# You do not need an api key for Quotation APIs
print(UPBitClient.get_markets()) 

api_key = 'your api key'
api_secret = 'a very secret key'

c = UPBitClient(api_key, api_secret)
print(c.accounts)
```
