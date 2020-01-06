class WasInFamilyUtilities:
    def CheckConfigUpToDate(self):
        """
        Used to check the saved config file to the current working document
        if they dont match then it promps you to set the config properly for
        the current document.
        
        CHECKS WHETHER FAMILIES ARE LOADED INTO THE DOC OR NOT
        """
        # Save when the config was set.
        projectInfo = self.doc.ProjectInformation
        projectId = projectInfo.Id.IntegerValue
        projectName = None
        for p in projectInfo.Parameters:
            if p.Definition.Name == "Project Name":
                projectName = p.AsString()

        todaysDate = ("{0}-{1}-{2}".format(dt.Today.Month, dt.Today.Day, dt.Today.Year))

        configProjectName = self.currentConfig["projectName"]
        configProjectId = self.currentConfig["projectId"]
        configDate = self.currentConfig["configDate"]
        
        # a nested conditional format is used here if (set of conditions) or (set of conditions)
        if ((projectName != configProjectName or projectId != configProjectId)
            or (projectId == configProjectId and todaysDate != configDate)):
            self.storefront_set_config()
        else:
            self.SFLoadFamilies(True)