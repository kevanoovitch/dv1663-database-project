

-- CREATE DATABASE IF NOT EXISTS BookTracker;

DROP TABLE Books;

 -- DROP TABLE Authors, Books, Users, Genres, BookGenres, UserBooks;

CREATE TABLE IF NOT EXISTS Authors (
	AuthorID INT PRIMARY KEY AUTO_INCREMENT,
	Name VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS Books (
	BookID INT PRIMARY KEY AUTO_INCREMENT,
	Title varchar(1000),
	PublishedYear INT,
	AuthorID INT,  
	FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID)
);

CREATE TABLE IF NOT EXISTS Users (
	UserID INT PRIMARY KEY AUTO_INCREMENT, 
	Username varchar(20),
	Email varchar(50),
	isAdmin BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Genres (
	GenreID INT PRIMARY KEY AUTO_INCREMENT,
	GenreName VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS BookGenres (
	ID INT PRIMARY KEY AUTO_INCREMENT,
	BookID INT,                          
    GenreID INT,
	FOREIGN KEY (BookID) REFERENCES Books(BookID),
	FOREIGN KEY (GenreID) REFERENCES Genres(GenreID)
);

CREATE TABLE IF NOT EXISTS UserBooks (
	UserbookID INT PRIMARY KEY AUTO_INCREMENT,
	UserID INT, 
	BookID INT,
	status varchar(50),
	rating INT,
	review varchar(500), 
	dateAdded DATE, 
	FOREIGN KEY (BookID) REFERENCES Books(BookID),
	FOREIGN KEY (UserID) REFERENCES Users(UserID)
);





