import re 

def ReplaceWords(strin):
    transcriber = {'&ExponentialE;': '&#x2147;', '&Integral;': '&#x222B;', '&DifferentialD;': '&#x2146;'}
    for symbol in transcriber:

        strin = re.sub(symbol, transcriber[symbol], strin) 

    return strin
    
def matches(strin):

    pattern = re.compile('&.+?;')
    if pattern.search(strin) == None:

        return strin

    for case in re.findall('(&.+?;\s?)', strin):
        #print(re.search('(&.+?;\s?)', strin).groups())
        operator = re.search("(?<=&)(.+?)(?=;)", case).group(0)
        strin = re.sub(case, '<mchar name="{}" />'.format(operator), strin)
    
    return strin

if __name__ == "__main__":
    
    expr = matches("""
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mo>&#x222B;</mo>
  <mo>(</mo>
  <mn>2</mn>
  <msup>
    <mi>x</mi>
    <mn>2</mn>
  </msup>
  <mo>-</mo>
  <mn>6</mn>
  <mi>x</mi>
  <mo>-</mo>
  <mn>2</mn>
  <mo>)</mo>
  <mrow>
    <mo>&#x2146;</mo>
    <mi>x</mi>
  </mrow>
</math>
    """)
    print(expr)