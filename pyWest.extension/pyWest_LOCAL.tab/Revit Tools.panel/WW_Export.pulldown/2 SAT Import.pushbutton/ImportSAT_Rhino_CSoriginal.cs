// Decompiled with JetBrains decompiler
// Type: ImportSATasFF18.ImportSATasFF18
// Assembly: ImportSATasFF18, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
// MVID: 6722977A-6F99-41BA-8B7C-75A08C5F3084
// Assembly location: C:\Users\aluna\Documents\WeWork Code\ImportSATasFF18.dll

using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using System.Collections;
using System.Collections.Generic;

namespace ImportSATasFF18
{
  [Transaction]
  internal class ImportSATasFF18 : IExternalCommand
  {
    public Result Execute(
      ExternalCommandData commandData,
      ref string message,
      ElementSet elements)
    {
      Document document = commandData.get_Application().get_ActiveUIDocument().get_Document();
      FileOpenDialog fileOpenDialog = new FileOpenDialog("SAT file (*.sat)|*.sat");
      ((FileDialog) fileOpenDialog).set_Title("Select SAT file to import");
      ((FileDialog) fileOpenDialog).Show();
      ModelPath selectedModelPath = ((FileDialog) fileOpenDialog).GetSelectedModelPath();
      ((FileDialog) fileOpenDialog).Dispose();
      string userVisiblePath = ModelPathUtils.ConvertModelPathToUserVisiblePath(selectedModelPath);
      SATImportOptions satImportOptions = new SATImportOptions();
      View element = new FilteredElementCollector(document).OfClass(typeof (View)).ToElements()[0] as View;
      try
      {
        using (Transaction transaction = new Transaction(document, "Import SAT"))
        {
          transaction.Start();
          ElementId elementId = document.Import(userVisiblePath, satImportOptions, element);
          using (IEnumerator<GeometryObject> enumerator1 = document.GetElement(elementId).get_Geometry(new Options()).GetEnumerator())
          {
            while (((IEnumerator) enumerator1).MoveNext())
            {
              using (IEnumerator<GeometryObject> enumerator2 = (enumerator1.Current as GeometryInstance).get_SymbolGeometry().GetEnumerator())
              {
                while (((IEnumerator) enumerator2).MoveNext())
                {
                  Solid current = enumerator2.Current as Solid;
                  FreeFormElement.Create(document, current);
                }
              }
            }
          }
          document.Delete(elementId);
          transaction.Commit();
        }
        return (Result) 0;
      }
      catch
      {
        TaskDialog.Show("Error Importing", "Something went wrong");
        return (Result) -1;
      }
    }
  }
}
