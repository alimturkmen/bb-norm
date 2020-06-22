import re

import entity


def parse_bb_label_file(file_path):
    search_labels = entity.SearchLabel()

    with open(file_path, encoding='utf-8') as file:
        lines = re.split("\n", file.read())

        for line in lines:
            result = re.search(".*OntoBiotope.*(T[0-9]*) Referent:OBT:([0-9]*)", line)
            if result is not None:
                search_labels.add(result.group(1), result.group(2))
            else:
                result = re.search(".*NCBI_Taxonomy.*(T[0-9]*) Referent:([0-9]*)", line)
                if result is not None:
                    search_labels.add(result.group(1), result.group(2))

    return search_labels


def parse_bb_a1_file(file_path):
    search_entities = []
    with open(file_path, encoding='utf-8') as file:
        lines = re.split("\n", file.read())

        for line in lines:
            for type in entity.EntityType:
                search_str = "(T[0-9]*)\t{} ([0-9]*) ([0-9]*)\t([A-Za-z0-9-_ \.β\/]*)".format(type.value)
                result = re.search(search_str, line)

                if result is not None:
                    search_entities.append(entity.SearchEntity(
                        result.group(1), entity.EntityType(type.value), result.group(4), int(result.group(2)),
                        int(result.group(3))
                    ))
                    break

    return search_entities


def parse_all_bb_norm_files(dev_files, dev_labels):
    all_entities = []
    all_labels = []

    for idx, dev_file in enumerate(dev_files):
        search_entities = parse_bb_a1_file(dev_file)
        search_labels = parse_bb_label_file(dev_labels[idx])
        true_labels = []

        for search_entity in search_entities:
            true_labels.append(search_labels.entities[search_entity.id])

        all_entities.append(search_entities)
        all_labels.append(true_labels)

    return all_entities, all_labels


def parse_ontobiotope_file(file_path):
    biotopes = {}

    with open(file_path, encoding='utf-8') as file:
        lines = re.split("\n", file.read())

        biotope = None
        print("Loading OntoBiotope file...")
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
                    biotope.name = line[6:]
                    biotope.name_list = list(filter(lambda x: len(x) > 0, biotope.name.split(' ')))

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
