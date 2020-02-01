# D) NO APPROPRIATE SELECTION MADE
else:
    mainDialog = TaskDialog("Hello, Revit!")
    mainDialog.MainInstruction = "Hello, Revit!"
    mainDialog.MainContent = "This sample shows how to use a Revit task dialog to communicate with the user. /nThe command links below open additional task dialogs with more information."

    # Add commmandLink options to task dialog
    mainDialog.AddCommandLink(TaskDialogCommandLinkId.CommandLink1, "View information about the Revit installation")
    mainDialog.AddCommandLink(TaskDialogCommandLinkId.CommandLink2,"View information about the active document")

    # Set common buttons and default button. If no CommonButton or CommandLink is added,
    # task dialog will show a Close button by default
    mainDialog.CommonButtons = TaskDialogCommonButtons.Close
    mainDialog.DefaultButton = TaskDialogResult.Close

    # Set footer text. Footer text is usually used to link to the help document.
    mainDialog.FooterText ="<a href=\"http://usa.autodesk.com/adsk/servlet/index?siteID=123112&id=2484975 \">" + "Click here for the Revit API Developer Center</a>"

    tResult = mainDialog.Show()