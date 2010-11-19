#!/usr/bin/python

#
# The simple minded object generator for Fortran
#

### includes
import os
import sys
import re
import string
import fileinput
import ConfigParser
from optparse import OptionParser


### defaults
comp_cmd="$(FC) $(FFLAGS) $(INCLUDES)"


### cmd args
opt_parser  = OptionParser()

opt_parser.add_option( "-o", "--output",
                       action = "store", type = "string",
                       dest = "output", default = 'Makefile.objdep',
                       help = "Output Makefile" )

opt_parser.add_option( "-f", "--fex",
                       action = "store", type = "string",
                       dest = "fex_arr", default = '\.F(90)?$:\.f(90)?$',
                       help = "Fortran extension patterns to scan" )

opt_parser.add_option( "-s", "--src",
                       action = "store", type = "string",
                       dest = "src_pat", default = 'src_.*',
                       help = "Source directory pattern" )

opt_parser.add_option( "-r", "--root",
                       action = "store", type = "string",
                       dest = "root_path", default = '.',
                       help = "Root directory" )

opt_parser.add_option( "-d", "--debug",
                        action = "store_true",
                        dest = "debug", default = False,
                        help = "Debug verbose" )
### process args
(options, args) = opt_parser.parse_args()
debug     = options.debug
src_pat   = options.src_pat
root_path = options.root_path
fex_arr   = options.fex_arr.split(":")
output    = options.output

### lookup tables
obj_db = {}
mod_db = {}


### functions
def brkstr( a, m = 5 ):
  r = ""
  c = 1
  l = len(a)
  for s in a:
    r += s+" "
    if c % m == 0 and l > m:
      r += "\\\n"
      c = 1
      l -= m - 1 
    # end if
    c += 1
  # end for
  return r
# end def


### BEGIN MAIN
try:
  MF = open( output, "w" )
except:
  print "Output error: " + output
  sys.exit(1)


print
print "Generate Object Dependencies"
print

for root, dirs, files in os.walk( root_path ):
  if debug:
    print
    print "DIR:",root

  if not ( root == "." or re.match( src_pat, os.path.basename( root ) ) ):
    continue

  for fn in files:
    fp   = os.path.join( root, fn )
    fbn  = os.path.basename( fn )
    fpa  = fp.split( "." )
    fpa[-1] = string.lower( fpa[-1] )
    fpl  = ".".join(fpa)

    for fex in fex_arr:
      if not re.match( ".*"+fex, fbn ):
        continue
      
      # build object database
      fon = re.sub( fex, ".o", fbn )
      if debug:
        print "%-32s : %s" % ( fon, fp )
        
      # search source
      tmp = []
      modules = []
      rules = {}
      uses = []
      includes = []
      for line in fileinput.input( fp ):
        line = line.strip()

        # infile rules
        pat = re.compile( "^!RULE +FC:.*", re.IGNORECASE )
        if re.match( pat, line ):
          tmp = line.split( ":" )
          rules["FC"] = tmp[1].strip()
        # end if

        pat = re.compile( "^!RULE +FFLAGS:.*", re.IGNORECASE )
        if re.match( pat, line ):
          tmp = line.split( ":" )
          rules["FFLAGS"] = tmp[1].strip()
        # end if

        pat = re.compile( "^!RULE +INCLUDES:.*", re.IGNORECASE )
        if re.match( pat, line ):
          tmp = line.split( ":" )
          rules["INCLUDES"] = tmp[1].strip()
        # end if

        # module
        pat = re.compile( "^MODULE +.*$", re.IGNORECASE )
        if re.match( pat, line ):
          tmp = line.split()
          if tmp[1] in modules:
            print "ERROR: MODULE",tmp[1]
          else:
            modules.append( tmp[1] )
            mod_db[tmp[1]] = fon
        # end if

        pat = re.compile( "^USE +.*$", re.IGNORECASE )
        if re.match( pat, line ):
          line = re.sub( ",.*$", "", line )
          tmp = line.split()
          if not tmp[1] in uses:
            uses.append( tmp[1] )
        # end if

        pat = re.compile( "^#?INCLUDE +.*$", re.IGNORECASE )
        if re.match( pat, line ):
          tmp = line.split()
          tmp[1] = re.sub( "\"", "", tmp[1] )
          if not tmp[1] in includes:
            includes.append( root+"/"+tmp[1] )
        # end if
      # end for line

      obj_db[fon] = { "path" : fpl, "opath" : fp, 
                      "module" : modules, "use" : uses, 
                      "include" : includes }

      if debug:
        if modules:
          print "  MODULE :", modules
        if uses:
          print "  USE :", uses
        if includes:
          print "  INCLUDE :", includes
        if "FC" in rules:
          obj_db[fon].update( { "rule_fc" : rules["FC"] } )
          print "  RULE FC:", rules["FC"]
        if "FFLAGS" in rules:
          obj_db[fon].update( { "rule_fflags" : rules["FFLAGS"] } )
          print "  RULE FFLAGS:", rules["FFLAGS"]
        if "INCLUDES" in rules:
          obj_db[fon].update( { "rule_includes" : rules["INCLUDES"] } )
          print "  RULE INCLUDES:", rules["INCLUDES"]
      # end if


    # end for fex

  # end for fn

# end for os.walk


# build object dependencies
MF.write( "### OBJECTS ###\n" )

objs = []
srcs = []

for obj in obj_db:
  dep = []
  dep.append( obj_db[obj]["opath"] )

  objs.append( obj )
  srcs.append( obj_db[obj]["opath"] )

  # use
  for use in obj_db[obj]["use"]:
    if use in mod_db:
      dep.append( mod_db[use] )
  # end for

  # include
  for inc in obj_db[obj]["include"]:
    dep.append( inc )
  # end for

  dep_str = brkstr( dep )
  MF.write( obj + " : " + dep_str + "\n" )

  # prepare compilation command
  ccmd = comp_cmd
  if "rule_fc" in obj_db[obj]:
    ccmd = ccmd.replace( "$(FC)", obj_db[obj]["rule_fc"] )
  if "rule_fflags" in obj_db[obj]:
    ccmd = ccmd.replace( "$(FFLAGS)", obj_db[obj]["rule_fflags"] )
  if "rule_includes" in obj_db[obj]:
    ccmd = ccmd.replace( "$(INCLUDES)", obj_db[obj]["rule_includes"] )

  MF.write( "\t"+ccmd+" -c "+obj_db[obj]["opath"]+" -o "+obj+"\n" )
# end for

MF.write( "\n\n### MiSC ###\n" )
MF.write( "OBJS = " + brkstr( objs ) + "\n\n" )
MF.write( "SRCS = " + brkstr( srcs ) + "\n\n" )

MF.close()
### END MAIN
