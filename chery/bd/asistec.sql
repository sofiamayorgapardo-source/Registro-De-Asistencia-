-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 19-08-2026 a las 00:24:06
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `asistec`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `acudiente`
--

CREATE TABLE `acudiente` (
  `Acu_CodAcudiente` int(11) NOT NULL,
  `Acu_TipoDocumento` int(10) DEFAULT NULL,
  `Acu_Nombre` varchar(50) NOT NULL,
  `Acu_Apellido` varchar(50) NOT NULL,
  `Acu_Parentesco` varchar(15) NOT NULL,
  `Acu_Telefono` int(11) DEFAULT NULL,
  `Acu_Correo` varchar(30) NOT NULL,
  `Acu_Direcion` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `arl`
--

CREATE TABLE `arl` (
  `Arl_CodArl` int(11) NOT NULL,
  `Arl_Nombre` varchar(50) NOT NULL,
  `Arl_Direcion` varchar(30) NOT NULL,
  `Arl_Telefono` int(11) DEFAULT NULL,
  `Arl_Correo` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asignatura`
--

CREATE TABLE `asignatura` (
  `Asi_CodAsignatura` int(11) NOT NULL,
  `Asi_NomAsignatura` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `docentes`
--

CREATE TABLE `docentes` (
  `Doc_CodDocentes` int(11) NOT NULL,
  `Doc_TipoDocumento` int(11) DEFAULT NULL,
  `Doc_Nombres` varchar(50) NOT NULL,
  `Doc_Apellidos` varchar(50) NOT NULL,
  `Doc_FechaNacimiento` varchar(15) NOT NULL,
  `Doc_Cod_Asignatura` int(11) DEFAULT NULL,
  `Doc_Telefono` int(11) DEFAULT NULL,
  `Doc_Correo` varchar(30) NOT NULL,
  `Doc_Direcion` varchar(50) NOT NULL,
  `Doc_Obcervacion` varchar(50) NOT NULL,
  `Doc_Genero` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `eps`
--

CREATE TABLE `eps` (
  `Eps_CodEps` int(11) NOT NULL,
  `Eps_Nombre` varchar(50) NOT NULL,
  `Eps_Telefono` int(11) DEFAULT NULL,
  `Eps_Direcion` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estudiantes`
--

CREATE TABLE `estudiantes` (
  `Est_CodEstudiante` int(11) NOT NULL,
  `Est_Cod_TipoDocumentos` int(11) DEFAULT NULL,
  `Est_Nombre` varchar(50) NOT NULL,
  `Est_Apellido` varchar(50) NOT NULL,
  `Est_FechaDeNacimiento` varchar(15) NOT NULL,
  `Est_Cod_Grado` int(10) DEFAULT NULL,
  `Est_Cod_Grupo` int(10) DEFAULT NULL,
  `Est_Correo` varchar(30) NOT NULL,
  `Est_Telefono` int(11) DEFAULT NULL,
  `Est_Direcion` varchar(30) NOT NULL,
  `Est_Cod_Eps` int(11) DEFAULT NULL,
  `Est_ObservacionMedica` varchar(100) NOT NULL,
  `Est_Cod_ArlEstudiantil` int(11) DEFAULT NULL,
  `Est_Cod_SedeEstudiantil` int(11) DEFAULT NULL,
  `Est_estrato` int(10) DEFAULT NULL,
  `Est_Gereno` varchar(20) NOT NULL,
  `Est_Cod_Acudiente` int(11) DEFAULT NULL,
  `Est_Cod_PadresFamilia` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `grado`
--

CREATE TABLE `grado` (
  `Gra_Codigo` int(11) NOT NULL,
  `Gra_NombreGrado` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `grupo`
--

CREATE TABLE `grupo` (
  `Gru_Codigo` int(11) NOT NULL,
  `Gru_NombreGrupo` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registroasistencia`
--

CREATE TABLE `registroasistencia` (
  `Reg_CodRegistroAsistencia` int(11) NOT NULL,
  `Reg_CodEstudiante` int(11) DEFAULT NULL,
  `Reg_CodDocente` int(11) DEFAULT NULL,
  `Reg_FechaHoraIngreso` varchar(30) NOT NULL,
  `Reg_Observacion` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registropadresfamilia`
--

CREATE TABLE `registropadresfamilia` (
  `Reg_CodPadresFamilia` int(11) NOT NULL,
  `Reg_TipoDeDocumento` int(11) DEFAULT NULL,
  `Reg_Nombres` varchar(50) NOT NULL,
  `Reg_Apellidos` varchar(50) NOT NULL,
  `Reg_Telefono` int(11) DEFAULT NULL,
  `Reg_Correo` varchar(30) NOT NULL,
  `Reg_Direccion` varchar(30) NOT NULL,
  `Reg_EmpresaTrabajo` varchar(50) NOT NULL,
  `Reg_Genero` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sedes`
--

CREATE TABLE `sedes` (
  `Sed_CodigoSede` int(11) NOT NULL,
  `Sed_NomSede` varchar(50) NOT NULL,
  `Sed_Direccion` varchar(30) NOT NULL,
  `Sed_Correo` varchar(30) NOT NULL,
  `Sed_Telefono` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipodocumento`
--

CREATE TABLE `tipodocumento` (
  `Tip_Codigo` int(11) NOT NULL,
  `Tip_TipoDocumento` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `acudiente`
--
ALTER TABLE `acudiente`
  ADD PRIMARY KEY (`Acu_CodAcudiente`);

--
-- Indices de la tabla `arl`
--
ALTER TABLE `arl`
  ADD PRIMARY KEY (`Arl_CodArl`);

--
-- Indices de la tabla `asignatura`
--
ALTER TABLE `asignatura`
  ADD PRIMARY KEY (`Asi_CodAsignatura`);

--
-- Indices de la tabla `docentes`
--
ALTER TABLE `docentes`
  ADD PRIMARY KEY (`Doc_CodDocentes`);

--
-- Indices de la tabla `eps`
--
ALTER TABLE `eps`
  ADD PRIMARY KEY (`Eps_CodEps`);

--
-- Indices de la tabla `estudiantes`
--
ALTER TABLE `estudiantes`
  ADD PRIMARY KEY (`Est_CodEstudiante`);

--
-- Indices de la tabla `grado`
--
ALTER TABLE `grado`
  ADD PRIMARY KEY (`Gra_Codigo`);

--
-- Indices de la tabla `grupo`
--
ALTER TABLE `grupo`
  ADD PRIMARY KEY (`Gru_Codigo`);

--
-- Indices de la tabla `registroasistencia`
--
ALTER TABLE `registroasistencia`
  ADD PRIMARY KEY (`Reg_CodRegistroAsistencia`);

--
-- Indices de la tabla `registropadresfamilia`
--
ALTER TABLE `registropadresfamilia`
  ADD PRIMARY KEY (`Reg_CodPadresFamilia`);

--
-- Indices de la tabla `sedes`
--
ALTER TABLE `sedes`
  ADD PRIMARY KEY (`Sed_CodigoSede`);

--
-- Indices de la tabla `tipodocumento`
--
ALTER TABLE `tipodocumento`
  ADD PRIMARY KEY (`Tip_Codigo`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
