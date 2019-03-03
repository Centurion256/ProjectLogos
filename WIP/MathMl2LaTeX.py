import os
import re
from regex_gen import ReplaceWords

def mml2latex(mml):
    """
    (str) -> str
    :param mml: mml code in str representation
    :return: string of LaTeX code
    """
    prefix = """
    <!DOCTYPE mml:math 
    PUBLIC "-//W3C//DTD MathML 2.0//EN"
           "http://www.w3.org/Math/DTD/mathml2/mathml2.dtd" [
    <!ENTITY % MATHML.prefixed "INCLUDE">
    <!ENTITY % MATHML.prefix "mml">
]>
<math xmlns="http://www.w3.org/1998/Math/MathML"
xsi="http://www.w3.org/2001/XMLSchema-instance"
schemaLocation="http://www.w3.org/1998/Math/MathML
    http://www.w3.org/Math/XMLSchema/mathml2/mathml2.xsd"> 
    """
    #<math xmlns="http://www.w3.org/1998/Math/MathML">    
    file = open("tmp.mml", "w", encoding='utf-8')
    if re.match("<math.*?>.+?</math>", mml) == None:

        mml = '<math xmlns="http://www.w3.org/1998/Math/MathML">{}</math>'.format(mml)
    else:

        mml = re.sub('<math.*?>', '<math xmlns="http://www.w3.org/1998/Math/MathML">', mml)

    #mml = mml.replace('&Integral;', '&#x222B;').replace('&DifferentialD;', '&#x2146;')
    reorganized = ReplaceWords(mml)
    print(reorganized, file=file)
    file.close()
    prompt = "xsltproc mathml_2_latex/mmltex.xsl " + "tmp.mml"
    return os.popen(prompt).read()

    