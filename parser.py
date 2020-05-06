import entity
import re


def parse_bb_norm_file(file_path):
    search_entities = []

    with open(file_path) as file:
        lines = re.split("\n", file.read())

        for line in lines:
            result = re.search("(T[0-9]*)\tHabitat [0-9]* [0-9]*\t([A-Za-z0-9-_ \.]*)", line)
            if result is not None:
                search_entities.append(entity.SearchEntity(result.group(1), entity.EntityType("Habitat"), result.group(2)))

    return search_entities


def parse_ontobiotope_file(file_path):
    biotopes = {}

    with open(file_path) as file:
        lines = re.split("\n", file.read())

        biotope = None

        for line in lines:
            if line == "[Term]":
                biotope = entity.Biotope()
            elif line == "":
                if biotope is not None:
                    biotopes[biotope.id] = biotope
                    biotope = None
            else:
                result = re.search("([a-z_]*?):", line)

                if result is None:
                    continue

                word = result.group(1)

                if word == "id":
                    # Extract the id part, eg 'id: OBT:000123', output will be '000123'
                    biotope.id = line[8:8 + 6]
                elif word == "name":
                    # Extract the name part, eg 'name: hola', output will be 'hola'
                    biotope.name = line[6:-1]
                    biotope.name_list = biotope.name.split(' ')
                elif word == "synonym":
                    # Get the part after 'synonym: '
                    remaining = line[len(word) + 2:-1]

                    result = re.search("\"([a-z -_]*)\" ([A-Z]*)", remaining)
                    if result is None:
                        print("Unknown character sets")
                    else:
                        biotope.synonyms.append(entity.Synonym(entity.SynonymType(result.group(2)), result.group(1)))
                elif word == "is_a":
                    # Extract the id part, eg 'id: OBT:000123', output will be '000123'
                    biotope.is_as.append(line[10:10 + 6])

    return biotopes
