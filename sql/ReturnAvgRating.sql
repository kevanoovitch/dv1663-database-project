CREATE DEFINER=`root`@`localhost` FUNCTION `BookTracker`.`ReturnAvgRating`(p_bookID INT) RETURNS decimal(3,2)
    READS SQL DATA
    DETERMINISTIC
BEGIN
	DECLARE avg_rating DECIMAL(3,2);

	SELECT AVG(rating)
	INTO avg_rating
	FROM UserBooks 
	WHERE BookID = p_bookID AND rating IS NOT NULL;

	RETURN avg_rating;
END