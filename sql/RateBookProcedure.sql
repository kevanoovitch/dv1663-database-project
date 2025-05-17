CREATE DEFINER=`root`@`localhost` PROCEDURE `BookTracker`.`RateBookProcedure`(
	IN p_userID INT,
    IN p_bookID INT,
    IN p_rating INT,
    IN p_review VARCHAR(500)
)
BEGIN
    DECLARE existingID INT;

    SELECT UserBookID INTO existingID
    FROM UserBooks
    WHERE UserID = p_userID AND BookID = p_bookID;

    IF existingID IS NULL THEN
        INSERT INTO UserBooks (UserID, BookID, status, dateAdded)
        VALUES (p_userID, p_bookID, 'Read', CURDATE());
    END IF; 

    UPDATE UserBooks 
    SET rating = p_rating, 
        review = p_review
    WHERE UserID = p_userID AND BookID = p_bookID;
END