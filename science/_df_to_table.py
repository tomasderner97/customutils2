def parse_column_property(cp):

    col_name = cp[0]
    if len(cp) >= 2:
        quantity_name = cp[1]
    else:
        quantity_name = col_name
    if len(cp) >= 3:
        unit = cp[2]
    else:
        unit = ""
    if len(cp) >= 4:
        float_format = cp[3]
    else:
        float_format = None

    return col_name, quantity_name, unit, float_format


def find_table_format_for_S_col(float_format):
    """
    parse float_format (for pandas to_string method) to find S[table-format=?]
    """
    import re

    table_format = ""  # S column needs info about digits before and after decimal .
    result = re.search("{:(.+)}", float_format)  # {:2.2f} -> 2.2f
    table_format = ""
    if result:
        table_format = result.group(1)
        if table_format[0] == ".":
            table_format = "1" + table_format
        if "f" in table_format or "F" in table_format:  # like 2.2f
            table_format = table_format[:-1]  # 2.2
        elif "e" in table_format or "E" in table_format:  # like 2.2e
            table_format += "1"  # -> 2.2e1
    if table_format:
        return f"S[table-format={table_format}]"
    else:
        return "S"


def make_column_strings_equal_length(quantity_name, unit, str_data):
    """ 
    finds lenght of the longest string in column and fills others to that length,
    quantity and unit aligned left and data right
    """

    len_of_longest = len(max(str_data + [quantity_name, unit], key=len))

    right_adjust = f"{{:>{len_of_longest}}}".format
    right_adjusted = [right_adjust(s) for s in str_data]
    left_adjust = f"{{:<{len_of_longest}}}".format
    quantity_name = left_adjust(quantity_name)
    unit = left_adjust(unit)

    return [quantity_name, unit] + right_adjusted


def make_formater_from_S_col_format_string(format_string):

    fmt = format_string

    if "e" in format_string:
        fmt = format_string.split("e")[0] + "e"
    else:
        fmt += "f"

    return f"{{:{fmt}}}".format


def df_to_booktabs_table(df, column_properties, file=None):
    """
    Parameters
    ----------
    df : pd.DataFrame
    column_properties : sequence of sequences of size 3 or 4
        description of columns. The inner sequences should be 
        [
            name_of_col_in_df, 
            optional_name_of_quantity, 
            optional_unit, 
            optional_S_col_fmt_str
        ] 
        S column formater examples: 1.2, 4.3e1
    file : str
        path to file to save this in. Default is None - no saving

    Returns
    -------
    formated table with booktabs in latex code
    """

    columns = []
    col_types = []

    for cp in column_properties:

        col_name, quantity_name, unit, S_col_format = parse_column_property(cp)

        if col_name == "index":
            from pandas import Series
            series = Series(df.index.values)
        else:
            series = df[col_name]
        s_column = series.dtype.name != "object"

        if s_column:
            col_type = f"S[table-format={S_col_format}]"
            col_types.append(col_type)
        else:
            col_types.append("l")

        float_format = make_formater_from_S_col_format_string(
            S_col_format
        ) if S_col_format else None

        col_of_strings = series.to_string(
            index=False,
            float_format=float_format
        ).split("\n")

        unit = f"[{unit}]"
        if s_column:
            quantity_name = f"{{{quantity_name}}}"
            unit = f"{{{unit}}}"

        finished_column_list = make_column_strings_equal_length(quantity_name, unit, col_of_strings)

        columns.append(finished_column_list)

    rows = zip(*columns)
    concatenated_rows = [" & ".join(r) + r" \\" for r in rows]

    concatenated_rows[1] += r" \midrule"
    concatenated_rows[-1] += r" \bottomrule"

    header = [r"\begin{tabular}[t]{"]
    for ct in col_types:
        header.append(f"  {ct}")
    header.append(r"} \toprule")

    footer = [r"\end{tabular}"]

    finished = "\n".join(header + concatenated_rows + footer)

    if file:
        with open(file, "w+") as f:
            f.write(finished)

    return finished
