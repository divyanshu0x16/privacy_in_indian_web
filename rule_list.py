import string

def get_rules():
    with open('easylist.txt', 'r') as file:
        lines = file.readlines()

    generic_selectors = []
    domain_specific_rules = {}

    for line in lines:

        if line[0] != '#' and not line[0].isalnum():
            continue

        if '##' not in line:
            continue

        parts = line.split('##')
        domains = parts[0].split(',')
        selector = parts[1]

        if domains[0] != '':
            for domain in domains:
                if domain in domain_specific_rules:
                    domain_specific_rules[domain].append(selector)
                else:
                    domain_specific_rules[domain] = [selector]
        else:
            generic_selectors.append(selector)

    return (generic_selectors, domain_specific_rules)
