import wikipediaapi
wiki = wikipediaapi.Wikipedia('pl')
page = wiki.page('21_grudnia')

def print_sections(sections, level=0):
        for s in sections:
                print("%s: %s - %s" % ("*" * (level + 1), s.title, s.text[0:40]))
                print_sections(s.sections, level + 1)

print_sections(page.sections)
print(page.sections)
