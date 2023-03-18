import re
#raw_record = '{name: John, age: 30, city: New York}\n'
raw_record = '<title>The Great Gatsby</title><author>F. Scott Fitzgerald</author><publisher>Charles Scribners Sons</publisher><year>1925</year>\n'
#raw_record = '[book][title]The Great Gatsby[/title][author]F. Scott Fitzgerald[/author][publisher]Charles Scribners Sons[/publisher][year]1925[/year][/book]\n'

separador = ','
#field_template = 'H:V'
field_template = '<H>V</H>'
clip_start = 0
clip_end = 0
# recorto los clip_start primeros caracteres y los clip_end ultimos caracteres de raw_record
print(raw_record)
raw_record = raw_record.strip()
if clip_start > 0:
    raw_record = raw_record[clip_start:]
if clip_end > 0:
    raw_record = raw_record[:-clip_end]
# Elimino comillas
raw_record = raw_record.replace('"', '')
print(raw_record)
# '<(\w+)>(.+?)</\1>'
#special_chars = ['[',']','(',')','{','}','|','^','$','.','*','+','?']
special_chars = ['[',']','(',')','{','}']
expression = field_template
for char in special_chars:
    expression = expression.replace(char, '\\'+char)
print(expression)

expression = expression.replace('H', '(\w+)',1)
expression = expression.replace('V', '([\w\s.]+)',1)
# expression = expression.replace('V', '(.+?)',1)
expression = expression.replace('H', '\\1',1)

print(expression)

pattern = re.compile(expression)
matches = pattern.findall(raw_record)
print(dict(matches))
