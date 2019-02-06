SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `japanesebot`
--

-- --------------------------------------------------------

--
-- Structure of the `Texts` table
--

CREATE TABLE `Texts` (
  `text_id` int(11) NOT NULL,
  `chat_id` int(11) NOT NULL,
  `type` varchar(20) NOT NULL,
  `language_og` varchar(3) NOT NULL,
  `contentbefore` varchar(512) DEFAULT NULL,
  `contentafter` varchar(512) DEFAULT NULL,
  `timestamp_txt` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- --------------------------------------------------------

--
-- Structure of the `Users` table
--

CREATE TABLE `Users` (
  `chat_id` int(11) NOT NULL,
  `username` varchar(128) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;


--
-- Index for the `Texts` table
--
ALTER TABLE `Texts`
  ADD PRIMARY KEY (`text_id`),
  ADD KEY `ChiaveSecondaria` (`chat_id`);

--
-- Index for the `Users` table
--
ALTER TABLE `Users`
  ADD PRIMARY KEY (`chat_id`);

--
-- AUTO_INCREMENT for the `Texts` table
--
ALTER TABLE `Texts`
  MODIFY `text_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;


--
-- Limits for the `Texts` table
--
ALTER TABLE `Texts`
  ADD CONSTRAINT `ChiaveSecondaria` FOREIGN KEY (`chat_id`) REFERENCES `Users` (`chat_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
