# <summary>
# Create new table type
# Type Name: 1200x750x380mm
# Parameters to change:
# Width = 1200
# Depth = 750
# Height = 380
# Top Material = Glass
# Leg Material = Glass
# </summary>
"""
FamilySymbol CreateNewType( FamilySymbol oldType )
{
  FamilySymbol sym = oldType.Duplicate(
    _type_name ) as FamilySymbol;

  SetElementParameterInMm( sym, "Width", 1200 );
  SetElementParameterInMm( sym, "Depth", 750 );
  SetElementParameterInMm( sym, "Height", 380 );

  Element material_glass = Util.FindElementByName(
    sym.Document, typeof( Material ), "Glass" );

  ElementId id = material_glass.Id;

  sym.get_Parameter( "Top Material" ).Set( id );
  sym.get_Parameter( "Leg Material" ).Set( id );

  return sym;
}
"""

def CreateNewType(oldType):
  if type(oldType) is FamilySymbol:
    sym = oldType.Duplicate(_type_name)
  
  SetElementParameterInMm(sym, "Width", 1200)
  SetElementParameterInMm(sym, "Depth", 750)
  SetElementParameterInMm(sym, "Height", 380)
  
  glass = Util.FindElementByName(sym.Document, Material, "Glass")
  
  id = material_glass.Id
  
  # GET SET MAY BE VERY IMPORTANT
  sym.get_Parameter("Top Material").Set(id)
  sym.get_Parameter("Leg Material").Set(id)
  
  return(sym)



# family retrieval and new type creation test
# Retrieve existing type or create new

FamilySymbol symbol = Util.FindElementByName( doc, typeof( FamilySymbol ), _type_name ) as FamilySymbol ?? CreateNewType( tables[0].Symbol );

"""
FormsAuth = formsAuth ?? new FormsAuthenticationWrapper();
expands to:

FormsAuth = formsAuth != null ? formsAuth : new FormsAuthenticationWrapper();
which further expands to:

if(formsAuth != null)
    FormsAuth = formsAuth;
else
    FormsAuth = new FormsAuthenticationWrapper();
"""