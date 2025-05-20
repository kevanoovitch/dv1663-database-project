

-- CREATE DATABASE IF NOT EXISTS BookTracker;



DROP TABLE Authors, Books, Users, Genres, BookGenres, UserBooks,BookAuthors;




CREATE TABLE IF NOT EXISTS Authors (
	AuthorID INT PRIMARY KEY AUTO_INCREMENT,
	Name VARCHAR(175)
);

CREATE TABLE IF NOT EXISTS Books (
	BookID INT PRIMARY KEY AUTO_INCREMENT,
	Title varchar(1000),
	PublishedYear INT
);

CREATE TABLE IF NOT EXISTS Users (
	UserID INT PRIMARY KEY AUTO_INCREMENT, 
	Username varchar(20),
	Email varchar(50),
	isAdmin BOOLEAN DEFAULT FALSE
);



CREATE TABLE IF NOT EXISTS Genres (
	GenreID INT PRIMARY KEY AUTO_INCREMENT,
	GenreName VARCHAR(55)
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

CREATE TABLE BookAuthors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    BookID INT,
    AuthorID INT,
    FOREIGN KEY (BookID) REFERENCES Books(BookID),
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID)
);

SELECT b.Title, g.GenreName
FROM Books b
JOIN BookGenres bg ON b.BookID = bg.BookID
JOIN Genres g ON bg.GenreID = g.GenreID
WHERE g.GenreName = 'Science Fiction';

SELECT b.Title, g.GenreName
FROM Books b
JOIN BookGenres bg ON b.BookID = bg.BookID
JOIN Genres g ON bg.GenreID = g.GenreID
WHERE LOWER(g.GenreName) = 'science fiction';




