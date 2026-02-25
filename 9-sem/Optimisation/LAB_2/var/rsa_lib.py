# Python Program for implementation of RSA Algorithm


def power(base, expo, m):
    res = 1
    base = base % m
    while expo > 0:
        if expo & 1:
            res = (res * base) % m
        base = (base * base) % m
        expo = expo // 2
    return res

def encrypt(m, e, n):
    return power(m, e, n)

def encrypt_array(nums,e,n):
    r = []
    for num in nums:
        r.append(encrypt(num,e,n))
    return r

# text-text, e - public key, n - mod
def encrypt_text(text,e,n):
    return encrypt_array(chars_to_int(text),e,n)

def decrypt(c, d, n):
    return power(c, d, n)

def decrypt_array(nums,d,n):
    r=[]
    for num in nums:
        r.append(decrypt(num,d,n))
    return r

# nums - array of number, d - private key, n - mod
def decrypt_text(nums,d,n):
    return ''.join(int_to_chars(decrypt_array(nums,d,n)))

def chars_to_int(text):
    r = []
    for t in text:
        r.append(ord(t))
    return r

def int_to_chars(num):
    text=[]
    for n in num:
        text.append(chr(n))
    return text
