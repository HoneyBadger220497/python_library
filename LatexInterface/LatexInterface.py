# -*- coding: utf-8 -*-
# Autor: Joachim Pomper
# Created: 04.05.2019
# Updated: 09.05.2019
# by: Joachim oPomper

### Import module and from modules #############################################
import numpy as np
import subprocess
import os
################################################################################

# path of pdflatex exe on Pc
dir_pdf_latex = r'C:/texlive/2018/bin/win32/pdflatex'

### Define Classes #############################################################
class Tabular:
    def __init__(this, values, uncertainty, alignment = 'horizontal'):
        """Tabular(values, uncertainty, alignment = 'horizontal'):
        Initiates instance of class Latex_Interface.Tabular()

        INPUT:
        - required:
            values      <list> : Both can be a nested list or a list of
            uncertainty <list>   numpy.ndarrays. They have to be of same size.
        - optional:
             alignment  <str>  : String that determines the Alignment of the
                                 Tabular. Must either be 'horizontal' or
                                 'vertical'
        """
        ## Input parse ##
        n_col, n_row = _InputParseTabular.test_init( values,
                                                     uncertainty,
                                                     alignment)

        ## Setup tablular content from input data as horizontal table ##
        data = []; # init list
        # create list of (value, uncertaity) tuples and collect
        # them in nested list.
        for val, unc in zip(values, uncertainty):
            if not any(unc):
                unc = [0]*len(val)
            row = [(v,u) for v, u in zip(val, unc)]
            row = row + [()]*(n_col - len(row)) # fill up with empty tupels
            data.append(row)

        ## public attributes ##
        this.content = data
        this.row_names = [str(int+1) for int in range(n_row)]
        this.col_names = [str(int+1) for int in range(n_col)]
        this.row_col_name = " "

        ## private format attributes ##
        this.n_col = n_col              # number of columns
        this.n_row = n_row              # number of rows
        this.disp_col_names = False     # flag: if true -> print col_names
        this.disp_row_names = False     # flag: if true -> print row_names
        this.cell_space = 16            # number of signs used for each tabular
                                        # entry when printed

        # change alignment of tabular if nescessary
        if alignment == 'vertical':
            this.switchAlignment()

    def switchAlignment(this):
        """.switchAlignment()
        Changes the Table from vertical to horizontal alignment
        and vic versa"""
        # Swap columnnames and rownames of tablular
        this.row_names, this.col_names = this.col_names, this.row_names
        # transpose entries of tabular
        data = [[]]*this.n_col # initiate data list
        for idx_col in range(this.n_col):
            col = []
            for idx_row in range(this.n_row):
                col.append(this.content[idx_row][idx_col])
            data[idx_col] = col
        this.content = data
        # swap number of columns and rows
        this.n_row, this.n_col = this.n_col, this.n_row

    def config(this, disp_col_names = False, disp_row_names = False ):
        """.config(disp_col_names = False, disp_row_names = False ):
        Used to change visibility settings for .print() methods of a
        instance of class \"Tabular\" """
        ## Input Parse ##
        _InputParseTabular.test_config(disp_col_names, disp_row_names)

        ## change Settings ##
        this.disp_col_names = disp_col_names
        this.disp_row_names = disp_row_names

    def editColNames(this, names):
        # input parse
        _InputParseTabular.test_addNames(names, this.n_col)

        # update col_names
        n_names = len(names)
        if n_names == this.n_col + 1:
            this.row_col_name = names[0]
            this.col_names = names[1:]
        else:
            this.col_names[0:n_names] = names

        # update cell space
        cs = this.cell_space
        for name in names:
            cs = max(cs, len(name))
        this.cell_space = cs

        # display column names in printed table
        this.disp_col_names = True

    def editRowNames(this, names):
        # input parse
        _InputParseTabular.test_addNames(names, this.n_row)

        # update col_names
        n_names = len(names)
        if n_names == this.n_row + 1:
            this.row_col_name = names[0]
            this.row_names = names[1:]
        else:
            this.row_names[0:n_names] = names

        # update cell space
        cs = this.cell_space
        for name in names:
            cs = max(cs, len(name))
        this.cell_space = cs

        # display row names in printed Table
        this.disp_row_names = True

    def print(this, cs=0, delimiter = ',', pm = ' +- '):
        """.print( cs=0, delimiter = ',', pm = ' +- ')
        Used to print the tabular in the consol
        INPUT:
        optional:
            cs          <int> (1,): Value to overwrite cell space property
            delimiter   <str> (1,): Value to set delimiter sign for numbers
            pm          <str> (n,): Value to set plusminus sign between value
                                    and uncertainty """
        ## Input parse ##
        # recalculate cs
        if not cs : #check if cs is 0, empty or false
            cs = this.cell_space #use default variable
        if  cs%2 != 0:
            cs = cs+1

        ## Print head line with column names ##
        if this.disp_col_names:
            row_str = " | "
            if this.disp_row_names:
                row_str = row_str + this.str2Tabularcell(this.row_col_name, cs)
                row_str = row_str + " | "
            for col_name in this.col_names:
                cell = this.str2Tabularcell(col_name, cs)
                row_str = row_str + cell + " | "
            print(row_str)

        ## Print table body ##
        for row, row_name in zip(this.content , this.row_names):
            row_str = " | "

            if this.disp_row_names:
                cell = this.str2Tabularcell(row_name, cs)
                row_str = row_str + cell + " | "

            for item in row:
                if type(item) is tuple:
                    cell = this.tupel2Tabularcell(item, cs, delimiter, pm)
                elif type(item) is str:
                    cell = this.str2Tabularcell(item, cs)
                row_str = row_str + cell + " | "
            print(row_str)

    def tupel2Tabularcell(this, in_tuple, cs=10, delimiter = '.', pm = ' +- '):
        """.tupel2Tabularcell(in_tupel, cs=10, delimiter = '.', pm = ' +- '))
        Converts a (Value, Uncertaitny) Tupel into a string and also adjust
        the significant digits of the value to the significans of the
        given uncertainty.
        INPUT:
        required:
            in_tupel    <tuple> (2,) tupel with value and uncertainty.
                                     if uncertainty is 0, the value will be
                                     set to maximal 6 significant digits.
        optional:
            cs          <int> (1,)   number of signs used for output str 'cell'
            delimiter   <str> (1,)   string used as komma-dot, for insantce ','
            pm          <str> (n)    string use as plusminus sign between value
                                     and uncertainty
        OUTPUT:
            cell        <str> (cs,)  string of the form 'value +- uncertainty'
        """
        len_pm = len(pm)/2

        if in_tuple: #check if not emptyS
            val = in_tuple[0]
            unc = in_tuple[1]
            sig_d = 0
        else:
            unc = ' '

        if unc == ' ':
            cell = " " * cs
            # cell = " "*int(cs/2-1) + "  " + " "*int(cs/2-1)
        elif unc == 0:
            cell_str = "{:^" + str(cs) + ".6g}"
            cell = cell_str.format(val)
        elif int(unc) == 0:
            while int(unc) == 0:
                sig_d = sig_d + 1
                unc = unc * 10
            unc = round(unc)*10**(-sig_d)
            if unc*10**sig_d == 10 :
                sig_d = sig_d - 1
            unc_str = "{:<" + str(int(cs/2)-int(np.ceil(len_pm))) +".1g}"
            val_str = ("{:>" + str(int(cs/2)-int(np.floor(len_pm))) + "." +
                       str(sig_d) + "f}")
            cell = val_str.format(val) + pm + unc_str.format(unc)
        else:
            while int(unc) != 0:
                sig_d = sig_d + 1
                unc = unc/10
            unc =  round(unc*10)*10**(sig_d-1)
            unc = int(unc)
            if unc *10**-sig_d  == 1:
                sig_d = sig_d + 1
            val = round(val/10**(sig_d-1) ) * 10**(sig_d-1)
            val = int(val)
            unc_str = "{:<" + str(int(cs/2)-int(np.ceil(len_pm))) +"d}"
            val_str = "{:>" + str(int(cs/2)-int(np.floor(len_pm))) +"d}"
            cell = val_str.format(val) + pm + unc_str.format(unc)

        cell = cell.replace('.', delimiter)
        return cell

    def str2Tabularcell(this, in_str, cs):
        """.str2Tabularcell(in_str, cs)
        expands a given string with blanks so it has the size of an
        tabularcell string given by cs.
        """
        cell_str = "{:^" +str(cs)+ "s}"
        cell = cell_str.format(in_str)

        return cell

    def addColumn(this, values, uncertainty = [], pos = [], name = 'new_col'):

        ## Input parse ##
        _InputParseTabular.test_addData( values, uncertainty,
                                        pos, this.n_row, name)
        ## add data ##
        if not uncertainty:
            uncertainty = [0]*len(values)

        data = []
        for val, unc in zip(values, uncertainty):
            if type(val) is str:
                data.append(val)
            else:
                data.append((val, unc))

        if not pos:
            pos = this.n_col
        else:
            pos = pos - 1

        for row, item in zip(this.content, data):
            row.insert(pos, item)

        ## add Column name ##
        this.col_names.insert(pos, name)

        ## adjust number of columns ##
        this.n_col = this.n_col + 1

        ## adjust cell space variable
        this.cell_space = max(this.cell_space, len(name))

    def addRow(this, values, uncertainty = [], pos = [], name = 'new_row'):

        ## Input parse ##
        _InputParseTabular.test_addData(values, uncertainty,
                                        pos, this.n_col, name)

        ## add data ##
        if not uncertainty:
            uncertainty = [0]*len(values)

        data = []
        for val, unc in zip(values, uncertainty):
            if type(val) is str:
                data.append(val)
            else:
                data.append((val, unc))

        if not pos:
            pos = this.n_row
        else:
            pos = pos - 1

        this.content.insert(pos, data)

        ## add Column name ##
        this.row_names.insert(pos, name)

        ## adjust number of columns ##
        this.n_row = this.n_row + 1

        ## adjust cell space variable
        this.cell_space = max(this.cell_space, len(name))

class LatexTabular(Tabular):

    def __init__(this, values, uncertainty, alignment = 'horizontal'):
        super().__init__(values, uncertainty, alignment)

    def write(this, filename, mode = "w+", delimiter = ',' , encoding = 'utf8'):

        file = open(filename, mode, encoding = encoding)
        this.__write_tabular_to_file(file, delimiter)
        file.close()

    def preview(this, delimiter = ','):

        cwd = os.getcwd()
        file_path = os.path.join(cwd, "tmp_tabular_preview.tex")
        file = open(file_path, "w+", encoding = 'utf8')
        file.write( "\\documentclass[11pt]{scrartcl} \n" +\
                    "\\usepackage[utf8]{inputenc} \n" +\
                    "\\usepackage[german]{babel} \n" +\
                    "\\usepackage[T1]{fontenc} \n" +\
                    "\\usepackage{float} \n \n" )
        file.write( "\\begin{document} \n \n")

        file.write( "\\begin{table} \n" + \
                    "\\caption{Preview of created Table} \n" + \
                    "\\centering")
        file.write( "\\begin{tabular}")
        n_col = this.n_col if this.disp_row_names else this.n_col - 1
        file.write( "{" + "c|"*(n_col) +"c} \\hline \\hline \n")

        this.__write_tabular_to_file(file, delimiter)

        file.write( "\\\\ \\hline \\hline \n")
        file.write( "\\end{tabular} \n" +\
                    "\\end{table} \n \n"   )

        file.write("\\end{document}")
        file.close()

        subprocess.check_call([dir_pdf_latex, file_path])
        pdf_file_path = os.path.join(cwd, 'tmp_tabular_preview.pdf' )
        os.remove(os.path.join(cwd, "tmp_tabular_preview.tex"))
        os.remove(os.path.join(cwd, "tmp_tabular_preview.aux"))
        os.remove(os.path.join(cwd, "tmp_tabular_preview.log"))
        pdf_view = subprocess.Popen(['tmp_tabular_preview.pdf'],shell=True)
        pdf_view.wait()

    def __write_tabular_to_file(this, file, delimiter = ','):

        cs = this.cell_space
        pm = r"~\pm~"

        if this.disp_col_names:
            if this.disp_row_names:
                row_col_name = this.str2Tabularcell(this.row_col_name, cs)
                file.write(row_col_name + " & ")
            for idx_col, col_name in enumerate(this.col_names):
                cell = this.str2Tabularcell(col_name, cs)
                cell = "  " + cell + "  "
                file.write(cell)
                if idx_col < this.n_col - 1:
                    file.write(" & ")
                else:
                    file.write(" \\\\ \\hline \n")
        for idx_row, row in enumerate(this.content):

            if this.disp_row_names:
                row_name = this.row_names[idx_row]
                cell = this.str2Tabularcell(row_name, cs)
                cell = cell + " & "
                file.write(cell)

            for idx_item, item in enumerate(row):

                if type(item) is tuple:
                    cell = this.tupel2Tabularcell(item, cs, delimiter, pm)
                    cell = "$ " + cell +" $"
                elif type(item) is str:
                    cell = this.str2Tabularcell(item, cs+4)
                file.write(cell)

                if idx_item < this.n_col - 1:
                    file.write(" & ")
                elif idx_row < this.n_row -1:
                    file.write(" \\\\ \n")

### Input Parse ################################################################

# define costume exception
class DimensionError(Exception):
    """ This error is raised if an input array has an unexpected size """
    pass

# input parser for tabular class
class _InputParseTabular:
    """ InputParser for class Latex_Interface.Tabular
    This is a static class """

    def test_init(values, uncertainty, alignment):
        "Input parse for the method '__init__' of class Latex_Interface.Tabular"


        if type(values) is not list:
            msg = ( "Input \"values\" has to be of type \"list\"")
            raise TypeError(msg)
        n_row = len(values)
        n_col = 0

        if type(uncertainty) is not list:
            msg = ( "Input \"uncertainty\" has to be of type \"list\"")
            raise TypeError(msg)

        if n_row != len(uncertainty):
            msg = ( "Input \"uncertainty\" has to be of same lenght"
                    "as imput \"values\" ")
            raise DimensionError(msg)

        for idx, val, unc in zip(range(n_row), values, uncertainty):
            if type(val) is np.ndarray:
                if np.shape(val) != (len(val),):
                    msg = ( "Input \values\" must not contain more " +
                            "more dimensional 'numpy.ndarrays'! ")
            elif type(val) is not list:
                msg = ( "Input \"values\" has to be nested list or a"
                        "list of numpy.ndarrays")
                raise TypeError(msg)

            if type(unc) is np.ndarray:
                if np.shape(unc) != (len(unc),):
                    msg = ( "Input \"uncertainty\" must not contain more " +
                            "more dimensional 'numpy.ndarrays'! ")
            elif type(unc) is not list:
                msg = ( "Input \"uncertainty\" has to be list of list"
                        "or numpy.ndarrays")
                raise TypeError(msg)

            if (len(unc) != len(val)) and (len(unc) != 0):
                msg = ( "All lists or numpy.ndarrays nested in \"values\" "
                        "and \"uncertainty\" have to be of same size pairwise. "
                        "If it is intended that there is no uncertaity for"
                        "one column/row, hand an empty list")
                raise DimensionError(msg)

            # calculate number of columns of table
            n_col = max(n_col, len(val))

        if type(alignment) is not str:
            msg = ( "Input \"alignment\" has to of type \"string\" ")
            raise TypeError(msg)

        if not (alignment == 'horizontal' or alignment == 'vertical'):
            msg = ( "Value of Input \"alignment\" has to be either 'horizontal'"
                    "or 'vertical'. ")
            raise ValueError(msg)

        ## Return ##
        return n_col, n_row

    def test_config(disp_col_names, disp_row_names):
        "Input parse for the method 'config' of class Latex_Interface.Tabular"

        if type(disp_col_names) is not bool:
            msg = "Input \"disp_col_names\" has to be of type \"bool\" "
            raise TypeError(msg)

        if type(disp_row_names) is not bool:
            msg = "Input \"disp_row_names\" has to be of type \"bool\" "
            raise TypeError(msg)

    def test_addNames(names, n_names):
        """Input parse for the methods 'editColNames' and 'editRowNames' of
        class Latex_Interface.Tabular."""

        # check type of input
        if  type(names) is not list:
            msg = ( "Input 'names' has to be a list of strings")
            raise ValueError(msg)
        for name in names:
            if type(name) is not str:
                msg = ( "Input 'names' has to be a list of strings")
                raise ValueError(msg)

        # check length of input
        if len(names) > n_names + 1:
            msg = ( "There are only" + str(n_names + 1) +
                    "columns that can be named!" )
            raise ValueError(msg)

    def test_addData(values, uncertainty, pos, n_values, name):
        """Input parse for the method 'addColumn' and 'addRow' of class
        Latex_Interface.Tabular"""

        if type(values) is np.ndarray:
            if np.shape(values) != (len(values),):
                msg = ( "Input \"Values\" must not contain more " +
                        "more dimensional 'numpy.ndarrays'! ")
        elif type(values) is not list:
            msg = ( "Input \"Values\" has to be a list containing strings or" +
                   "numbers or has to be a numpy.ndarray")
            raise TypeError(msg)

        if type(uncertainty) is np.ndarray:
            if np.shape(uncertainty) != (len(uncertainty),):
                msg = ( "Input \"uncertainty\" must not contain more " +
                        "more dimensional 'numpy.ndarrays'! ")
        elif type(uncertainty) is not list:
            msg = ( "Input \"uncertainty\" has to be a list containing " +
                    "strings or numbers or has to be a numpy.ndarray!")
            raise TypeError(msg)

        if not(0 <= pos <= n_values):
            msg = ( "Input \"pos\" out of range!")
            raise ValueError(msg)

        if len(values) > n_values:
            msg = ( "Input \"values\" has too many elements!")
            raise DimensionError(msg)

        if len(uncertainty) > n_values:
            msg = ( "Input \"uncertainty\" has too many elemtes!")
            raise DimensionError(msg)

        if len(values) != len(uncertainty) and uncertainty :
            msg = ( "Input \"uncertainty\" und Input \"values\" have to be " +
                    "of same length!")
            raise DimensionError(msg)

        if type(name) is not str:
            msg = ( "Input \"name\" has to be of type 'str'!")
            raise TypeError(msg)
