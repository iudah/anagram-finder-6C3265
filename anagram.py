import re

def clean_input(text):
    cleaned=  re.sub(r"[\W_ ]", r"", text.lower())
    return cleaned, "".join(sorted(cleaned))

def is_anagram(text1,text2):
    clean1,sort1=clean_input(text1)
    clean2,sort2=clean_input(text2)
    return sort1==sort2 and clean1!=clean2, sort1 if sort1==sort2 else None

if __name__ =="__main__":
    print(clean_input("There are some people we ususally don't like to meet in life. A number of them are crazy, foolish, or unwise."))
    str1, str2 = "Is a Dormitory", "Isa Dirty room"
    print(is_anagram(str1, str2))
    print(is_anagram(str1, str1))
