from enums import sources_base


# Basic random oversampling.
# Pick random samples from the minority class until you get the number of documents in the majority class.
# For 2 classes :  'relevant' , 'not relevant'

# TODO general to any n number of classes
def basic_oversampling(df_docs):
    print("     Function: basic_oversampling")
    only_relevant = df_docs[df_docs[sources_base.LABEL] == "relevant"]
    only_no_relevant = df_docs[df_docs[sources_base.LABEL] == "no_relevant"]

    number_relevants = len(only_relevant.index)
    number_no_relevants = len(only_no_relevant.index)
    difference = abs(number_no_relevants - number_relevants)
    minority_class = "relevant" if number_relevants < number_no_relevants else "no_relevant"

    if number_relevants > number_no_relevants:
        print("     -> ", difference, "random docs pick from the minority class (", minority_class, ")")
        extras = only_no_relevant.sample(difference, replace=True)
    else:
        extras = only_relevant.sample(difference, replace=True)

    return df_docs.append(extras, ignore_index=True)


class TypeOversampling:
    BASIC = basic_oversampling
