#!/usr/bin/env python

import sys, os, glib
import collections
import sqlite3 as lite
import pygtk  
import gtk  
import gtk.glade 

# Gui Class
class movieManager:
   wTree = None
   
   genreListSelected = []
   
   CURRENT_LIST_VIEW = 'icon'
   MOVIE_LIST_VIEW_LABEL = "list view";
   MOVIE_ICON_VIEW_LABEL = "icon view";
   
   def __init__( self ):
      try:
         self.wTree = gtk.Builder()
         self.wTree.add_from_file("gui/main.glade")
         
         #Create the genre treeView
         self.createGenreListView()
         
         #Create the movieView
         self.search_callback(self)
                
         dic = { 
                 "search_callback"  :  self.search_callback,
                 "set_movie_view" : self.bindMovieListView,
                 "on_windowMain_destroy" : self.quit
               }
         
         self.wTree.connect_signals( dic )
         self.wTree.get_object("toolbutton6")
         window = self.wTree.get_object("windowMain")
         window.show_all()
      except:
         print "Unexpected error:", sys.exc_info()[0]
         #raise
         #print("Unable to load GUI GT Glade")
         sys.exit(1)
   
   
   
   #set movie list view
   def bindMovieListView(self, button):
      buttonLabel = button.get_label()
      
      if(buttonLabel == self.MOVIE_LIST_VIEW_LABEL):
         if button.get_active():
            self.CURRENT_LIST_VIEW = "list"
      
      elif(buttonLabel == self.MOVIE_ICON_VIEW_LABEL):
         if button.get_active():
            self.CURRENT_LIST_VIEW = "icon" 
            
      #search movie
      self.search_callback(self)     
         
   #Create the genre treeView   
   def createGenreListView(self):
      self.treeviewGenre = self.wTree.get_object("treeviewGenre")
      #it create the gtk.TreeViewColumn and then set some needed properties
      title = "Genre"
      columnId = 0
      column = gtk.TreeViewColumn(title, gtk.CellRendererText() , text=columnId)
      column.set_resizable(True)      
      column.set_sort_column_id(columnId)
      column.set_property('visible', False)#hide the genre column
      self.treeviewGenre.append_column(column)
      
      column = gtk.TreeViewColumn('column2', gtk.CellRendererText(), text=1)   
      column.set_clickable(True)   
      column.set_resizable(True)   
      self.treeviewGenre.append_column(column)
      
      
      self.genreList = gtk.ListStore(str, str)
      self.treeviewGenre.set_model(self.genreList) 
      tree_selection = self.treeviewGenre.get_selection()
      tree_selection.set_mode(gtk.SELECTION_MULTIPLE)      
      # Bind clicked event
      #self.treeviewGenre.connect('button-press-event' , self.genreClickEvent)
      
      tree_selection.connect('changed',lambda s: self.genreClickEvent(s))
      
      #load treeview data
      imdbObj = Imdb()
      genreModelData = imdbObj.getGenreList()
      self.genreList.clear() 
      for row in genreModelData:
        genreName  = row[0]
        genreCount = str(row[1])
        genreDesc  = row[0]+" ("+str(row[1])+")"
        
        self.genreList.append([genreName, genreDesc])
   
   #Genre slected function
   def genreClickEvent(self, treeselection):
      genreList = []
   
      (model,pathlist) = treeselection.get_selected_rows()
      for path in pathlist :
          tree_iter = model.get_iter(path)
          genreValue = model.get_value(tree_iter,0)
      
          genreList.append(genreValue)

      self.genreListSelected = genreList

      #call the movie search
      self.search_callback(self)
        
      
   #Create the Movies iconView   
   def createMoviesListView(self, condition=""):
      DEFAULT_MOVIE_IMAGE = 'default_movie_photo.jpg'
      
      #hide the list view movies
      self.iconviewMovie = self.wTree.get_object("treeviewMovie").hide()
      
      #Create the movieView
      self.iconviewMovie = self.wTree.get_object("iconviewMovie")
      self.liststoreMovie = gtk.ListStore(str, gtk.gdk.Pixbuf)
      
      self.iconviewMovie.set_model(self.liststoreMovie)
      self.iconviewMovie.set_text_column(0)
      self.iconviewMovie.set_pixbuf_column(1)
      self.iconviewMovie.show()
      
      #register bottom movie details view event
      self.iconviewMovie.set_selection_mode(gtk.SELECTION_SINGLE)
      #self.iconviewMovie.connect('button-press-event', self.showMoveDtailsView)
      self.iconviewMovie.connect('selection-changed', self.showMoveDtailsView)
      self.iconviewMovie.connect('item-activated', self.showMoveDtailsView)
      
      
      imdbObj = Imdb()
      moviesModelData = imdbObj.getMoviesList(condition)
      
      for movie in moviesModelData:
         movieName      = movie[0]
         movieImageId   = movie[2]
         movieImageFile = "images/" + movieImageId + ".jpg"
         
         
         if not os.path.exists(movieImageFile):
            movieImageFile = DEFAULT_MOVIE_IMAGE
            
         
         # Create a tuple with image files
         try:
             pixbuf = gtk.gdk.pixbuf_new_from_file(movieImageFile)
             pix_w = pixbuf.get_width()
             pix_h = pixbuf.get_height()
             new_h = pix_h
             #new_h = (pix_h * 140) / pix_w   # Calculate the scaled height before resizing image
             scaled_pix = pixbuf.scale_simple(pix_w, new_h, gtk.gdk.INTERP_TILES)
             self.liststoreMovie.append((movieName, scaled_pix))
             
         except glib.GError:
             print "image not found:"
   
   def showMoveDtailsView(self, widget):
      path = widget.get_selected_items()
      
      print widget.select_path(path)
      
      ##if right click activate a pop-up menu
      #if event.button == 3 :
      #   self.popup.popup(None, None, None, None, event.button, event.time)
      ##if left click, activate the item to execute
      #if event.button == 1 :
      #   #self.iv_icon_activated(widget, path)
      #   self.popup.popup(None, None, None, None, event.button, event.time)
   
      

   #Create the movie treeView   
   def createMoviesListTreeView(self, condition=""):
     
      #hide the icon view movies
      self.iconviewMovie = self.wTree.get_object("iconviewMovie").hide()
   
      self.treeviewMovie = self.wTree.get_object("treeviewMovie")
      #it create the gtk.TreeViewColumn and then set some needed properties
      
      #Image column
      cell   = gtk.CellRendererPixbuf()
      column = gtk.TreeViewColumn("Photo", cell)
      column.add_attribute(cell, "pixbuf", 0)
      self.treeviewMovie.append_column(column)

      #Name column
      column = gtk.TreeViewColumn("Name", gtk.CellRendererText() , text=1)
      column.set_resizable(True)
      self.treeviewMovie.append_column(column)

      #Desc column      
      cell = gtk.CellRendererText()
      column = gtk.TreeViewColumn('desc', cell, text=2)
      column.set_clickable(True)   
      column.set_resizable(True)         
      self.treeviewMovie.append_column(column)
      
      self.treeviewMovie.show()
      
      self.listStoreMovie = gtk.ListStore(gtk.gdk.Pixbuf, str, str)
      self.treeviewMovie.set_model(self.listStoreMovie) 
      tree_selection = self.treeviewMovie.get_selection()
      
      #tree_selection.connect('changed',lambda s: self.genreClickEvent(s))
      
      #load treeview data
      imdbObj = Imdb()
      moviesModelData = imdbObj.getMoviesList(condition)
      
      for movie in moviesModelData:
         movieName      = movie[0]
         movieImageId   = str(movie[6])
         movieImageFile = "images/" + movieImageId + ".jpg"
        
         
         if not os.path.exists(movieImageFile):
            movieImageFile = 'default_movie_photo.jpg'
         

         pixbuf = gtk.gdk.pixbuf_new_from_file(movieImageFile)
         pix_w = pixbuf.get_width()
         pix_h = pixbuf.get_height()
         new_h = pix_h
         scaled_pix = pixbuf.scale_simple(pix_w, new_h, gtk.gdk.INTERP_TILES)
         
         self.listStoreMovie.append((pixbuf, movieName, movieImageId))

   
   
   
          
   def search_callback(self, widget):
      condition  =  " WHERE 1 "
      sortBy     =  "name"
      sortOrder  =  "ASC"
      userFilter = "all"
      #add search code here
      searchText = self.wTree.get_object("entry1").get_text()
      
      #search by text
      if searchText != "":
         condition = condition + " AND name LIKE '%"+searchText+"%'";
         
      #search by genre
      if len(self.genreListSelected) > 0:
         genreCondition = ""
         for thisGenre in self.genreListSelected:
            if thisGenre != "All":
               genreCondition = genreCondition + " AND genres LIKE '%"+thisGenre+"%'"             
         
         condition = condition + genreCondition
         
      #glu all sql condition, sort and order   
      condition = condition + " ORDER BY "+sortBy+" "+sortOrder;
      
      #tooltip advance
      #http://www.daa.com.au/pipermail/pygtk/2004-February/006954.html

      
      
      if(self.CURRENT_LIST_VIEW == 'icon'):
         self.createMoviesListView(condition)
      elif(self.CURRENT_LIST_VIEW == 'list'):
         self.createMoviesListTreeView(condition)
      else:
         self.createMoviesListView(condition)
      
   def add(self, widget):
      try:
         thistime = adder( self.wTree.get_object("inputEntry1").get_text(), self.wTree.get_object("inputEntry2").get_text() )
         self.wTree.get_object("warningHbox").hide()
         self.wTree.get_object("entryResult").set_text(thistime.giveResult())
      except ValueError:
         self.wTree.get_object("warningHbox").show()
         self.wTree.get_object("entryResult").set_text("ERROR")
         return 0
   
   def quit(self, widget):
      gtk.main_quit()
      sys.exit(0)

#IMDB Class
class Imdb:
   """This class represents all the wine information"""
   
   #cache data
   CACHE_GENRE_DATA          = [];
   CACHE_MOVIE_DATA = [];
   
   def __init__(self):
      self.genreList = []
      self.moviesList = []
      
      self.db = 'movies.db';
   
   def getDbconn(self):
      return lite.connect(self.db)
   
   #function for Genre List   
   def getGenreList(self):
      """This function returns a list of Movie Genre list"""
      allGenreList = []
      con = self.getDbconn()
      
      with con:    
         cur = con.cursor()    
         cur.execute("SELECT genres FROM movie_list")
         allGenresList  = cur.fetchall()

         #total movie count
         totalMovies = len(allGenresList)         
         
         for row in allGenresList:
            genres    = row[0].split(', ')
            genres = filter(None, genres)
            #allGenreList = list(set(allGenreList + genres))
            allGenreList  = allGenreList + genres
            #allGenreList = list(set(allGenreList + genres))
         

         
         #count genre with counter
         genreListCounter = collections.Counter(allGenreList)
         
         #make the counter to list item
         uniqueGenreList = genreListCounter.items() 
         
         # remove empty genre and Add "All" genre to the list
         #uniqueGenreList = filter(None, uniqueGenreList)
         uniqueGenreList.sort()
         uniqueGenreList.insert(0, ["All", totalMovies])
         
         
      return uniqueGenreList
      
   #function for Genre List   
   def getMoviesList(self, condition=""):
      """This function returns a list of Movies"""
      
      if len(self.CACHE_MOVIE_DATA) > 0:
         return self.CACHE_MOVIE_DATA
      else:      
         con = self.getDbconn()  
         with con:    
            cur = con.cursor()
            sqlText = "SELECT * FROM movie_list "+condition
            cur.execute(sqlText)
            self.moviesList = cur.fetchall()
         
            #set cache data
            self.CACHE_MOVIE_DATA = self.moviesList
            
         return self.moviesList
      
         
      
#create application 
if __name__ == "__main__":
   app = movieManager()
   gtk.main()
