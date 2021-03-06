-- phpMyAdmin SQL Dump
-- version 5.0.1
-- https://www.phpmyadmin.net/
--
-- Host: imdbdb
-- Generation Time: Aug 05, 2021 at 11:13 PM
-- Server version: 10.6.3-MariaDB-1:10.6.3+maria~focal
-- PHP Version: 7.4.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `imdbscrapper`
--
CREATE DATABASE IF NOT EXISTS `imdbscrapper` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `imdbscrapper`;

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`%` PROCEDURE `checkDuplicateIgnore` (IN `idCheck` BIGINT(20))  BEGIN
	SELECT ignoreList.idIgnore
    FROM ignoreList
    WHERE ignoreList.idIgnore = idCheck;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `checkDuplicateMovie` (IN `idCheck` BIGINT(20))  BEGIN
	SELECT movies.idMovie
    FROM movies
    WHERE movies.idMovie = idCheck;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `checkDuplicateRecheck` (IN `idCheck` BIGINT(20))  BEGIN
	SELECT recheck.idRecheck
    FROM recheck
    WHERE recheck.idRecheck = idCheck;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `checkDuplicateSerie` (IN `idCheck` BIGINT(20))  BEGIN
	SELECT series.idSerie
    FROM series
    WHERE series.idSerie = idCheck;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `getDuplicateMovies` ()  BEGIN
	SELECT movies.idMovie, movies.name
    FROM movies
    GROUP BY movies.name
    HAVING COUNT(movies.name) > 1;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `getDuplicateSeries` ()  BEGIN
	SELECT series.idSerie, series.name
    FROM series
    GROUP BY series.name
    HAVING COUNT(series.name) > 1;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `getMovieByName` (IN `movieName` VARCHAR(255))  BEGIN
	SELECT movies.idMovie, movies.name, movies.description, movies.imdbURL, movies.rating, movies.ratingCount, movies.releaseDate
    FROM movies
    WHERE movies.name = movieName;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `getMovies` (IN `valueRating` DOUBLE, IN `valueRatingCount` BIGINT(20), IN `valueReleaseDate` DATE)  BEGIN
		SELECT movies.idMovie, movies.name, movies.description, movies.imdbURL, movies.rating, movies.ratingCount, movies.releaseDate
    FROM movies
    WHERE movies.rating >= valueRating
    AND movies.ratingCount >= valueRatingCount
    AND movies.releaseDate  >= valueReleaseDate
    ORDER by movies.rating DESC, movies.ratingCount DESC;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `getSerieByName` (IN `serieName` VARCHAR(255))  BEGIN
	SELECT series.idSerie, series.name, series.description, series.imdbURL, series.rating, series.ratingCount, series.releaseDate
    FROM series
    WHERE series.name = serieName;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `getSeries` (IN `valueRating` DOUBLE, IN `valueRatingCount` BIGINT(20), IN `valueReleaseDate` DATE)  BEGIN
	SELECT series.idSerie, series.name, series.description, series.imdbURL, series.rating, series.ratingCount, series.releaseDate
    FROM series
    WHERE series.rating >= valueRating
    AND series.ratingCount >= valueRatingCount
    AND series.releaseDate  >= valueReleaseDate
    ORDER by series.rating DESC, series.ratingCount DESC;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `insertIgnore` (IN `inIDIgnore` BIGINT(20))  BEGIN
	INSERT INTO ignoreList
    (`idIgnore`)
    VALUES(inIDIgnore);
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `insertMovie` (`idMovie` BIGINT(20), `name` VARCHAR(255), `description` LONGTEXT, `imdbURL` VARCHAR(255), `rating` DOUBLE, `ratingCount` BIGINT(20), `releaseDate` DATE)  BEGIN
	INSERT INTO movies
    (`idmovie`, `name`, `description`, `imdbURL`, `rating`, `ratingCount`, `releaseDate`)
    VALUES(idMovie, name, description, imdbURL, rating, ratingCount, releaseDate);
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `insertMovieGenre` (IN `idMovie` BIGINT(20), IN `idGenre` VARCHAR(255))  BEGIN
	INSERT INTO moviesGenre
    (`idMovie`, `idGenre`)
    VALUES(idMovie, idGenre);
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `insertRecheck` (IN `inIDRecheck` BIGINT(20))  BEGIN
	INSERT INTO recheck
    (`idRecheck`)
    VALUES(inIDRecheck);
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `insertSerie` (`idSerie` BIGINT(20), `name` VARCHAR(255), `description` LONGTEXT, `imdbURL` VARCHAR(255), `rating` DOUBLE, `ratingCount` BIGINT(20), `releaseDate` DATE)  BEGIN
	INSERT INTO series
    (`idserie`, `name`, `description`, `imdbURL`, `rating`, `ratingCount`, `releaseDate`)
    VALUES(idSerie, name, description, imdbURL, rating, ratingCount, releaseDate);
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `insertSerieGenre` (IN `idSerie` BIGINT(20), IN `idGenre` VARCHAR(255))  BEGIN
	INSERT INTO seriesGenre
    (`idSerie`, `idGenre`)
    VALUES(idSerie, idGenre);
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `removeDuplicateMovie` (IN `inMovie` BIGINT(20), IN `inName` VARCHAR(255))  BEGIN
	DELETE FROM movies
    WHERE movies.idMovie = inMovie;
    DELETE FROM moviesGenre
    WHERE moviesGenre.idMovie = inMovie;
    INSERT INTO duplicateMovies
    (duplicateMovies.idMovie, duplicateMovies.nameMovie)
    VALUES (inMovie, inName);
    INSERT INTO ignoreList
    (ignoreList.idIgnore)
    VALUES (inMovie);
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `removeDuplicateSerie` (IN `inSerie` BIGINT(20), IN `inName` VARCHAR(255))  BEGIN
	DELETE FROM series
    WHERE series.idSerie = inSerie;
    DELETE FROM seriesGenre
    WHERE seriesGenre.idSerie = inSerie;
    INSERT INTO duplicateSeries
    (duplicateSeries.idSerie, duplicateSeries.nameSerie)
    VALUES (inSerie, inName);
    INSERT INTO ignoreList
    (ignoreList.idIgnore)
    VALUES (inSerie);
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `duplicateMovies`
--

CREATE TABLE `duplicateMovies` (
  `idMovie` bigint(20) NOT NULL,
  `nameMovie` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `duplicateSeries`
--

CREATE TABLE `duplicateSeries` (
  `idSerie` bigint(20) NOT NULL,
  `nameSerie` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `ignoreList`
--

CREATE TABLE `ignoreList` (
  `idIgnore` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `movies`
--

CREATE TABLE `movies` (
  `idMovie` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL,
  `imdbURL` varchar(255) NOT NULL,
  `rating` double DEFAULT NULL,
  `ratingCount` bigint(20) DEFAULT NULL,
  `releaseDate` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `moviesGenre`
--

CREATE TABLE `moviesGenre` (
  `id` bigint(20) NOT NULL,
  `idMovie` bigint(20) NOT NULL,
  `idGenre` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `recheck`
--

CREATE TABLE `recheck` (
  `idRecheck` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `series`
--

CREATE TABLE `series` (
  `idSerie` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL,
  `imdbURL` varchar(255) NOT NULL,
  `rating` double DEFAULT NULL,
  `ratingCount` bigint(20) DEFAULT NULL,
  `releaseDate` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `seriesGenre`
--

CREATE TABLE `seriesGenre` (
  `id` bigint(20) NOT NULL,
  `idSerie` bigint(20) NOT NULL,
  `idGenre` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `duplicateMovies`
--
ALTER TABLE `duplicateMovies`
  ADD PRIMARY KEY (`idMovie`);

--
-- Indexes for table `duplicateSeries`
--
ALTER TABLE `duplicateSeries`
  ADD PRIMARY KEY (`idSerie`);

--
-- Indexes for table `ignoreList`
--
ALTER TABLE `ignoreList`
  ADD PRIMARY KEY (`idIgnore`);

--
-- Indexes for table `movies`
--
ALTER TABLE `movies`
  ADD PRIMARY KEY (`idMovie`);

--
-- Indexes for table `moviesGenre`
--
ALTER TABLE `moviesGenre`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `recheck`
--
ALTER TABLE `recheck`
  ADD PRIMARY KEY (`idRecheck`);

--
-- Indexes for table `series`
--
ALTER TABLE `series`
  ADD PRIMARY KEY (`idSerie`);

--
-- Indexes for table `seriesGenre`
--
ALTER TABLE `seriesGenre`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `movies`
--
ALTER TABLE `movies`
  MODIFY `idMovie` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `moviesGenre`
--
ALTER TABLE `moviesGenre`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `series`
--
ALTER TABLE `series`
  MODIFY `idSerie` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `seriesGenre`
--
ALTER TABLE `seriesGenre`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
