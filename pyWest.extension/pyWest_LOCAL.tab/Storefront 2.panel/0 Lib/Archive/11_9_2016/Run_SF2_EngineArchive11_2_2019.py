def Run_SF2_Engine(self):
    # instantiate windows form
    storefrontConfig = SF2_GUI.Form(self.doc)
    storefrontConfig.Run_Form(printTest=True)
        
    # output from form
    userSettings = storefrontConfig.userSettings
    
    # load families
    SF2_Families.ParentClass(storefrontConfig).Run_SF2_Families()
    
    # PRE ERROR CHECK
    #SF2_Report.SFCheckModel().Run_SFvetModel(self.wallCLs)         

    # COLLECT SF WALLS
    #self.Run_CollectWalls()
    
    # RUN THAT WEIRD CLASS
    #self.Run_SomeClass()
    
    # CODE IN OPEN TRANSACTION
    #t = Transaction(self.doc, 'Generating Storefront Walls in Revit')
    #t.Start()
    #t.Commit()       

    # SECOND GUI FORM RUNS HERE

    # PARSE & SORT SF WALLS
    #self.Run_WallCLsOrganize(walls)

    # BUILD INITIAL SF GEO
    #self.Run_BuildCurtainWall()

    # MODIFY SF GEO
    #self.Run_ModifyCurtainWall()

    # POST ERROR CHECK - to be deprecated
    #print("...CHECKING ERRORS...")
    #SF2_Analysis.ErrorCheckingTools().SF_PostErrorCheck() # in overflow for now
    #print("...DONE!")
    

    # WRITE JSON REVIT -> CATIA
    
    
    # CREATE REPORT - save as json file