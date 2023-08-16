"""
    This module contains all of the common lists in the interface
    The properties are standard python lists of tuples containing three string values
    1-Look Up Value
    2-Human Readable Name
    3-Description (displayed when you hover your cursor over the value)
"""

PANEL_HEIGHTS = [
    ('115', '3H-4.53"', '3H-4.53'),
    ('147', '4H-5.79"', '4H-5.79'),
    ('179', '5H-7.05"', '5H-7.05'),
    ('211', '6H-8.31"', '6H-8.31'),
    ('243', '7H-9.57"', '7H-9.57'),
    ('275', '8H-10.83"', '8H-10.83'),
    ('307', '9H-12.09"', '9H-12.09'),
    ('339', '10H-13.35"', '10H-13.35'),
    ('371', '11H-14.61"', '11H-14.61'),
    ('403', '12H-15.87"', '12H-15.87'),
    ('435', '13H-17.13"', '13H-17.13'),
    ('467', '14H-18.39"', '14H-18.39'),
    ('499', '15H-19.65"', '15H-19.65'),
    ('531', '16H-20.91"', '16H-20.91'),
    ('563', '17H-22.17"', '17H-22.17'),
    ('595', '18H-23.43"', '18H-23.43'),
    ('627', '19H-24.69"', '19H-24.69'),
    ('659', '20H-25.94"', '20H-25.94'),
    ('691', '21H-27.20"', '21H-27.2'),
    ('723', '22H-28.46"', '22H-28.46'),
    ('755', '23H-29.72"', '23H-29.72'),
    ('787', '24H-30.98"', '24H-30.98'),
    ('819', '25H-32.24"', '25H-32.24'),
    ('851', '26H-33.50"', '26H-33.5'),
    ('883', '27H-34.76"', '27H-34.76'),
    ('915', '28H-36.02"', '28H-36.02'),
    ('947', '29H-37.28"', '29H-37.28'),
    ('979', '30H-38.54"', '30H-38.54'),
    ('1011', '31H-39.80"', '31H-39.8'),
    ('1043', '32H-41.06"', '32H-41.06'),
    ('1075', '33H-42.32"', '33H-42.32'),
    ('1107', '34H-43.58"', '34H-43.58'),
    ('1139', '35H-44.84"', '35H-44.84'),
    ('1171', '36H-46.10"', '36H-46.1'),
    ('1203', '37H-47.37"', '37H-47.37'),
    ('1235', '38H-48.62"', '38H-48.62'),
    ('1267', '39H-49.88"', '39H-49.88'),
    ('1299', '40H-51.14"', '40H-51.14'),
    ('1331', '41H-52.40"', '41H-52.4'),
    ('1363', '42H-53.66"', '42H-53.66'),
    ('1395', '43H-54.92"', '43H-54.92'),
    ('1427', '44H-56.18"', '44H-56.18'),
    ('1459', '45H-57.44"', '45H-57.44'),
    ('1491', '46H-58.70"', '46H-58.70'),
    ('1523', '47H-59.96"', '47H-59.96'),
    ('1555', '48H-61.22"', '48H-61.22'),
    ('1587', '49H-62.48"', '49H-62.48'),
    ('1619', '50H-63.74"', '50H-63.74'),
    ('1651', '51H-65.00"', '51H-65.0'),
    ('1683', '52H-66.26"', '52H-66.26'),
    ('1715', '53H-67.52"', '53H-67.52'),
    ('1747', '54H-68.78"', '54H-68.78'),
    ('1779', '55H-70.04"', '55H-70.04'),
    ('1811', '56H-71.30"', '56H-71.3'),
    ('1843', '57H-72.56"', '57H-72.56'),
    ('1875', '58H-73.82"', '58H-73.82'),
    ('1907', '59H-75.08"', '59H-75.08'),
    ('1939', '60H-76.34"', '60H-76.34'),
    ('1971', '61H-77.60"', '61H-77.6'),
    ('2003', '62H-78.86"', '62H-78.86'),
    ('2035', '63H-80.12"', '63H-80.12'),
    ('2067', '64H-81.38"', '64H-81.38'),
    ('2099', '65H-82.64"', '65H-82.64'),
    ('2131', '66H-83.90"', '66H-83.9'),
    ('2163', '67H-85.16"', '67H-85.16'),
    ('2195', '68H-86.42"', '68H-86.42'),
    ('2227', '69H-87.68"', '69H-87.68'),
    ('2259', '70H-88.94"', '70H-88.94'),
    ('2291', '71H-90.20"', '71H-90.2'),
    ('2323', '72H-91.46"', '72H-91.46'),
    ('2355', '73H-92.72"', '73H-92.72'),
    ('2387', '74H-93.98"', '74H-93.98'),
    ('2419', '75H-95.24"', '75H-95.24')
    ]


HOLE_HEIGHTS = {
    '115': '3H',
    '147': '4H',
    '179': '5H',
    '211': '6H',
    '243': '7H',
    '275': '8H',
    '307': '9H',
    '339': '10H',
    '371': '11H',
    '403': '12H',
    '435': '13H',
    '467': '14H',
    '499': '15H',
    '531': '16H',
    '563': '17H',
    '595': '18H',
    '627': '19H',
    '659': '20H',
    '691': '21H',
    '723': '22H',
    '755': '23H',
    '787': '24H',
    '819': '25H',
    '851': '26H',
    '883': '27H',
    '915': '28H',
    '947': '29H',
    '979': '30H',
    '1011': '31H',
    '1043': '32H',
    '1075': '33H',
    '1107': '34H',
    '1139': '35H',
    '1171': '36H',
    '1203': '37H',
    '1235': '38H',
    '1267': '39H',
    '1299': '40H',
    '1331': '41H',
    '1363': '42H',
    '1395': '43H',
    '1427': '44H',
    '1459': '45H',
    '1491': '46H',
    '1523': '47H',
    '1555': '48H',
    '1587': '49H',
    '1619': '50H',
    '1651': '51H',
    '1683': '52H',
    '1715': '53H',
    '1747': '54H',
    '1779': '55H',
    '1811': '56H',
    '1843': '57H',
    '1875': '58H',
    '1907': '59H',
    '1939': '60H',
    '1971': '61H',
    '2003': '62H',
    '2035': '63H',
    '2067': '64H',
    '2099': '65H',
    '2131': '66H',
    '2163': '67H',
    '2195': '68H',
    '2227': '69H',
    '2259': '70H',
    '2291': '71H',
    '2323': '72H',
    '2355': '73H',
    '2387': '74H',
    '2419': '75H'}

OPENING_HEIGHTS = [
    ('77.216', '3H-3.62"', '3H-3.62"'),
    ('109.220', '4H-4.88"', '4H-4.88"'),
    ('141.224', '5H-6.14"', '5H-6.14"'),
    ('173.228', '6H-7.40"', '6H-7.40"'),
    ('205.232', '7H-8.66"', '7H-8.66"'),
    ('237.236', '8H-9.92"', '8H-9.92"'),
    ('269.240', '9H-11.18"', '9H-11.18"'),
    ('301.244', '10H-12.44"', '10H-12.44"'),
    ('333.248', '11H-13.70"', '11H-13.70"'),
    ('365.252', '12H-14.96"', '12H-14.96"'),
    ('397.256', '13H-16.22"', '13H-16.22"'),
    ('429.260', '14H-17.48"', '14H-17.48"'),
    ('461.264', '15H-18.74"', '15H-18.74"'),
    ('493.268', '16H-20.00"', '16H-20.00"'),
    ('525.272', '17H-21.26"', '17H-21.26"'),
    ('557.276', '18H-22.52"', '18H-22.52"'),
    ('589.280', '19H-23.78"', '19H-23.78"'),
    ('621.284', '20H-25.04"', '20H-25.04"'),
    ('653.288', '21H-26.30"', '21H-26.30"'),
    ('685.292', '22H-27.56"', '22H-27.56"'),
    ('717.296', '23H-28.82"', '23H-28.82"'),
    ('749.300', '24H-30.08"', '24H-30.08"'),
    ('781.304', '25H-31.34"', '25H-31.34"'),
    ('813.308', '26H-32.60"', '26H-32.60"'),
    ('845.312', '27H-33.86"', '27H-33.86"'),
    ('877.316', '28H-35.12"', '28H-35.12"'),
    ('909.320', '29H-36.38"', '29H-36.38"'),
    ('941.324', '30H-37.64"', '30H-37.64"'),
    ('973.328', '31H-38.90"', '31H-38.90"'),
    ('1005.332', '32H-40.16"', '32H-40.16"'),
    ('1037.336', '33H-41.42"', '33H-41.42"'),
    ('1069.340', '34H-42.68"', '34H-42.68"'),
    ('1101.344', '35H-43.94"', '35H-43.94"'),
    ('1133.348', '36H-45.20"', '36H-45.20"'),
    ('1165.352', '37H-46.46"', '37H-46.46"'),
    ('1197.356', '38H-47.72"', '38H-47.72"'),
    ('1229.360', '39H-48.98"', '39H-48.98"'),
    ('1261.364', '40H-50.24"', '40H-50.24"'),
    ('1293.368', '41H-51.50"', '41H-51.50"'),
    ('1325.372', '42H-52.76"', '42H-53.66"'),
    ('1357.376', '43H-54.02"', '43H-54.02"'),
    ('1389.380', '44H-55.28"', '44H-55.28"'),
    ('1421.384', '45H-56.54"', '45H-56.54"'),
    ('1453.388', '46H-57.80"', '46H-57.80"'),
    ('1485.392', '47H-59.06"', '47H-59.06"'),
    ('1517.142', '48H-60.31"', '48H-60.31"'),
    ('1549.146', '49H-61.57"', '49H-61.57"'),
    ('1581.150', '50H-62.83"', '50H-62.83"'),
    ('1613.154', '51H-64.09"', '51H-64.09"'),
    ('1645.158', '52H-65.35"', '52H-65.35"'),
    ('1677.162', '53H-66.61"', '53H-66.61"'),
    ('1709.166', '54H-67.87"', '54H-67.87"'),
    ('1741.170', '55H-69.13"', '55H-69.13"'),
    ('1773.174', '56H-70.39"', '56H-70.39"'),
    ('1805.178', '57H-71.65"', '57H-71.65"'),
    ('1837.182', '58H-72.91"', '58H-72.91"'),
    ('1869.186', '59H-74.17"', '59H-74.17"'),
    ('1901.190', '60H-75.43"', '60H-75.43"'),
    ('1933.194', '61H-76.69"', '61H-76.69"'),
    ('1965.198', '62H-77.95"', '62H-77.95"'),
    ('1997.202', '63H-79.21"', '63H-79.21"'),
    ('2029.206', '64H-80.47"', '64H-80.47"'),
    ('2061.210', '65H-81.73"', '65H-81.73"'),
    ('2093.214', '66H-82.99"', '66H-82.99"'),
    ('2125.218', '67H-84.25"', '67H-84.25"'),
    ('2157.222', '68H-85.51"', '68H-85.51"'),
    ('2189.226', '69H-86.77"', '69H-86.77"'),
    ('2221.230', '70H-88.03"', '70H-88.03"'),
    ('2253.234', '71H-89.29"', '71H-89.29"'),
    ('2285.238', '72H-90.55"', '72H-90.55"'),
    ('2317.496', '73H-91.82"', '73H-91.82"'),
    ('2349.246', '74H-93.07"', '74H-93.07"'),
    ('2381.250', '75H-94.33"', '75H-94.33"'),
    ('2413.254', '76H-95.59"', '76H-95.59"')
    ]

PLANT_ON_TOP_OPENING_HEIGHTS = [
    ('32', '1H', '1.26"'),
    ('64', '2H', '2.52"'),
    ('96', '3H', '3.79"'),
    ('128', '4H', '5.04"'),
    ('160', '5H', '6.30"'),
    ('192', '6H', '7.56"'),
    ('224', '7H', '8.82"'),
    ('256', '8H', '10.08"'),
    ('288', '9H', '11.34"'),
    ('320', '10H', '12.60"'),
    ('352', '11H', '13.86"'),
    ('384', '12H', '15.12"'),
    ('416', '13H', '16.38"'),
    ('448', '14H', '17.64"'),
    ('480', '15H', '18.90"'),
    ('512', '16H', '20.16"'),
    ('544', '17H', '21.42"'),
    ('576', '18H', '22.68"'),
    ('608', '19H', '23.94"'),
    ('640', '20H', '25.20"'),
    ('672', '21H', '26.46"'),
    ('704', '22H', '27.72"'),
    ('736', '23H', '28.98"'),
    ('768', '24H', '30.24"'),
    ('800', '25H', '31.50"'),
    ('832', '26H', '32.76"'),
    ('864', '27H', '34.02"'),
    ('896', '28H', '35.28"'),
    ('928', '29H', '36.54"'),
    ('960', '30H', '37.80"'),
    ('992', '31H', '39.06"'),
    ('1024', '32H', '40.31"'),
    ('1056', '33H', '41.57"'),
    ('1088', '34H', '42.83"'),
    ('1120', '35H', '44.09"'),
    ('1152', '36H', '45.35"'),
    ('1184', '37H', '46.61"'),
    ('1216', '38H', '47.87"'),
    ('1248', '39H', '49.13"'),
    ('1280', '40H', '50.39"'),
    ('1312', '41H', '51.65"'),
    ('1344', '42H', '52.91"'),
    ('1376', '43H', '54.17"'),
    ('1408', '44H', '55.43"'),
    ('1440', '45H', '56.69"'),
    ('1472', '46H', '57.95"'),
    ('1504', '47H', '59.21"'),
    ('1536', '48H', '60.47"'),
    ('1568', '49H', '61.73"'),
    ('1600', '50H', '62.99"'),
    ('1632', '51H', '64.25"'),
    ('1664', '52H', '65.51"'),
    ('1696', '53H', '66.77"'),
    ('1728', '54H', '68.03"'),
    ('1760', '55H', '69.29"'),
    ('1792', '56H', '70.55"'),
    ('1824', '57H', '71.81"'),
    ('1856', '58H', '73.07"'),
    ('1888', '59H', '74.33"'),
    ('1920', '60H', '75.59"'),
    ('1952', '61H', '76.85"'),
    ('1984', '62H', '78.11"'),
    ('2016', '63H', '79.37"'),
    ('2048', '64H', '80.63"'),
    ('2080', '65H', '81.89"'),
    ('2112', '66H', '83.15"'),
    ('2144', '67H', '84.41"'),
    ('2176', '68H', '85.67"'),
    ('2208', '69H', '86.93"'),
    ('2240', '70H', '88.19"'),
    ('2272', '71H', '89.45"'),
    ('2304', '72H', '90.71"'),
    ('2336', '73H', '91.97"'),
    ('2368', '74H', '93.23"'),
    ('2400', '75H', '94.49"'),
    ('2432', '76H', '95.75"S')
    ]

DRAWER_BOTTOM_OFFSETS = [
    ('64', '2H-1.77"', '2H-1.77"'),
    ('96', '3H-3.03"', '3H-3.03"'),
    ('128', '4H-4.29"', '4H-4.29"'),
    ('160', '5H-5.55"', '5H-5.55"'),
    ('192', '6H-6.81"', '6H-6.81"'),
    ('224', '7H-8.07"', '7H-8.07"'),
    ('256', '8H-9.33"', '8H-9.33"'),
    ('288', '9H-10.59‬"', '9H-10.59‬"'),
    ('320', '10H-11.85"', '10H-11.85"'),
    ('352', '11H-13.11"', '11H-13.11"'),
    ('384', '12H-14.37"', '12H-14.37"'),
    ('416', '13H-15.63‬"', '13H-15.63‬"'),
    ('448', '14H-16.89‬"', '14H-16.89‬"'),
    ('480', '15H-18.15"', '15H-18.15"'),
    ('512', '16H-19.41"', '16H-19.41"'),
    ('544', '17H-20.67"', '17H-20.67"'),
    ('576', '18H-21.93"', '18H-21.93"'),
    ('608', '19H-23.19"', '19H-23.19"'),
    ('640', '20H-24.45"', '20H-24.45"'),
    ('672', '21H-25.71"', '21H-25.71"'),
    ('704', '22H-26.97"', '22H-26.97"'),
    ('736', '23H-28.23"', '23H-28.23"'),
    ('768', '24H-29.49‬"', '24H-29.49‬"'),
    ('800', '25H-30.75"', '25H-30.75"'),
    ('832', '26H-32.01"', '26H-32.01"'),
    ('864', '27H-33.27"', '27H-33.27"'),
    ('896', '28H-34.53"', '28H-34.53"'),
    ('928', '29H-35.79"', '29H-35.79"'),
    ('960', '30H-37.05‬"', '30H-37.05‬"'),
    ('992', '31H-38.31"', '31H-38.31"'),
    ('1024', '32H-39.56"', '32H-39.56"'),
    ('1056', '33H-40.82"', '33H-40.82"'),
    ('1088', '34H-42.08"', '34H-42.08"'),
    ('1120', '35H-43.34"', '35H-43.34"'),
    ('1152', '36H-44.6"', '36H-44.6"'),
    ('1184', '37H-45.86‬"', '37H-45.86‬"'),
    ('1216', '38H-47.12"', '38H-47.12"'),
    ('1248', '39H-48.38"', '39H-48.38"'),
    ('1280', '40H-49.64‬"', '40H-49.64‬"'),
    ('1312', '41H-50.9"', '41H-50.9"'),
    ('1344', '42H-52.16"', '42H-52.16"'),
    ('1376', '43H-53.42‬"', '43H-53.42"'),
    ]

SHELF_IN_DOOR_HEIGHTS = [
    ('76.962', '3H-3.03"', '3H-3.03"'),
    ('108.966', '4H-4.29"', '4H-4.29"'),
    ('140.97', '5H-5.55"', '5H-5.55"'),
    ('172.974', '6H-6.81"', '6H-6.81"'),
    ('204.978', '7H-8.07"', '7H-8.07"'),
    ('236.982', '8H-9.33"', '8H-9.33"'),
    ('268.986', '9H-10.59‬"', '9H-10.59‬"'),
    ('300.99', '10H-11.85"', '10H-11.85"'),
    ('332.994', '11H-13.11"', '11H-13.11"'),
    ('364.998', '12H-14.37"', '12H-14.37"'),
    ('397.002', '13H-15.63‬"', '13H-15.63‬"'),
    ('429.006', '14H-16.89‬"', '14H-16.89‬"'),
    ('461.01', '15H-18.15"', '15H-18.15"'),
    ('493.014', '16H-19.41"', '16H-19.41"'),
    ('525.018', '17H-20.67"', '17H-20.67"'),
    ('557.022', '18H-21.93"', '18H-21.93"'),
    ('589.026', '19H-23.19"', '19H-23.19"'),
    ('621.03', '20H-24.45"', '20H-24.45"'),
    ('653.034', '21H-25.71"', '21H-25.71"'),
    ('685.038', '22H-26.97"', '22H-26.97"'),
    ('717.042', '23H-28.23"', '23H-28.23"'),
    ('749.046', '24H-29.49‬"', '24H-29.49‬"'),
    ('781.05', '25H-30.75"', '25H-30.75"'),
    ('813.054', '26H-32.01"', '26H-32.01"'),
    ('845.058', '27H-33.27"', '27H-33.27"'),
    ('877.062', '28H-34.53"', '28H-34.53"'),
    ('909.066', '29H-35.79"', '29H-35.79"'),
    ('941.07', '30H-37.05‬"', '30H-37.05‬"'),
    ('973.074', '31H-38.31"', '31H-38.31"'),
    ('1005.078', '32H-39.56"', '32H-39.56"'),
    ('1037.082', '33H-40.82"', '33H-40.82"'),
    ('1069.086', '34H-42.08"', '34H-42.08"'),
    ('1101.09', '35H-43.34"', '35H-43.34"'),
    ('1133.094', '36H-44.6"', '36H-44.6"'),
    ('1165.098', '37H-45.86‬"', '37H-45.86‬"'),
    ('1197.102', '38H-47.12"', '38H-47.12"'),
    ('1229.106', '39H-48.38"', '39H-48.38"'),
    ('1261.11', '40H-49.64‬"', '40H-49.64‬"'),
    ('1293.114', '41H-50.9"', '41H-50.9"'),
    ('1325.118', '42H-52.16"', '42H-52.16"'),
    ('1357.122', '43H-53.42‬"', '43H-53.42"'),
    ]

FRONT_HEIGHTS = [
    ('91.948', '3H-3.62"', '3H-3.62"'),
    ('123.952', '4H-4.88"', '4H-4.88"'),
    ('155.956', '5H-6.14"', '5H-6.14"'),
    ('187.96', '6H-7.40"', '6H-7.40"'),
    ('219.964', '7H-8.66"', '7H-8.66"'),
    ('251.968', '8H-9.92"', '8H-9.92"'),
    ('283.972', '9H-11.18"', '9H-11.18"'),
    ('315.976', '10H-12.44"', '10H-12.44"'),
    ('347.98', '11H-13.70"', '11H-13.70"'),
    ('379.984', '12H-14.96"', '12H-14.96"')
    ]

# Uses the opening heights (Column 1) for placement but displays the height in panel height (Column 2 and 3).
ROD_HEIGHTS = [
    ('76.95', '3H-4.53"', '3H-4.53'),
    ('108.95', '4H-5.79"', '4H-5.79'),
    ('140.95', '5H-7.05"', '5H-7.05'),
    ('172.95', '6H-8.31"', '6H-8.31'),
    ('204.95', '7H-9.57"', '7H-9.57'),
    ('236.95', '8H-10.83"', '8H-10.83'),
    ('268.95', '9H-12.09"', '9H-12.09'),
    ('300.95', '10H-13.35"', '10H-13.35'),
    ('332.95', '11H-14.61"', '11H-14.61'),
    ('364.95', '12H-15.87"', '12H-15.87'),
    ('396.95', '13H-17.13"', '13H-17.13'),
    ('428.95', '14H-18.39"', '14H-18.39'),
    ('460.95', '15H-19.65"', '15H-19.65'),
    ('492.95', '16H-20.91"', '16H-20.91'),
    ('524.95', '17H-22.17"', '17H-22.17'),
    ('556.95', '18H-23.43"', '18H-23.43'),
    ('588.95', '19H-24.69"', '19H-24.69'),
    ('620.95', '20H-25.94"', '20H-25.94'),
    ('652.95', '21H-27.20"', '21H-27.2'),
    ('684.95', '22H-28.46"', '22H-28.46'),
    ('716.95', '23H-29.72"', '23H-29.72'),
    ('748.95', '24H-30.98"', '24H-30.98'),
    ('780.95', '25H-32.24"', '25H-32.24'),
    ('812.95', '26H-33.50"', '26H-33.5'),
    ('844.95', '27H-34.76"', '27H-34.76'),
    ('876.95', '28H-36.02"', '28H-36.02'),
    ('908.95', '29H-37.28"', '29H-37.28'),
    ('940.95', '30H-38.54"', '30H-38.54'),
    ('972.95', '31H-39.80"', '31H-39.8'),
    ('1004.95', '32H-41.06"', '32H-41.06'),
    ('1036.95', '33H-42.32"', '33H-42.32'),
    ('1068.95', '34H-43.58"', '34H-43.58'),
    ('1100.95', '35H-44.84"', '35H-44.84'),
    ('1132.95', '36H-46.10"', '36H-46.1'),
    ('1164.95', '37H-47.37"', '37H-47.37'),
    ('1196.95', '38H-48.62"', '38H-48.62'),
    ('1228.95', '39H-49.88"', '39H-49.88'),
    ('1260.95', '40H-51.14"', '40H-51.14'),
    ('1292.95', '41H-52.40"', '41H-52.4'),
    ('1324.95', '42H-53.66"', '42H-53.66'),
    ('1356.95', '43H-54.92"', '43H-54.92'),
    ('1388.95', '44H-56.18"', '44H-56.18'),
    ('1420.95', '45H-57.44"', '45H-57.44'),
    ('1452.95', '46H-58.70"', '46H-58.70'),
    ('1484.95', '47H-59.96"', '47H-59.96'),
    ('1516.95', '48H-61.22"', '48H-61.22'),
    ('1548.95', '49H-62.48"', '49H-62.48'),
    ('1580.95', '50H-63.74"', '50H-63.74'),
    ('1612.95', '51H-65.00"', '51H-65.0'),
    ('1644.95', '52H-66.26"', '52H-66.26'),
    ('1676.95', '53H-67.52"', '53H-67.52'),
    ('1708.95', '54H-68.78"', '54H-68.78'),
    ('1740.95', '55H-70.04"', '55H-70.04'),
    ('1772.95', '56H-71.30"', '56H-71.3'),
    ('1804.95', '57H-72.56"', '57H-72.56'),
    ('1836.95', '58H-73.82"', '58H-73.82'),
    ('1868.95', '59H-75.08"', '59H-75.08'),
    ('1900.95', '60H-76.34"', '60H-76.34'),
    ('1932.95', '61H-77.60"', '61H-77.6'),
    ('1964.95', '62H-78.86"', '62H-78.86'),
    ('1996.95', '63H-80.12"', '63H-80.12'),
    ('2028.95', '64H-81.38"', '64H-81.38'),
    ('2060.95', '65H-82.64"', '65H-82.64'),
    ('2092.95', '66H-83.90"', '66H-83.9'),
    ('2124.95', '67H-85.16"', '67H-85.16'),
    ('2156.95', '68H-86.42"', '68H-86.42'),
    ('2188.95', '69H-87.68"', '69H-87.68'),
    ('2220.95', '70H-88.94"', '70H-88.94'),
    ('2252.95', '71H-90.20"', '71H-90.2'),
    ('2284.95', '72H-91.46"', '72H-91.46'),
    ('2316.95', '73H-92.72"', '73H-92.72'),
    ('2348.95', '74H-93.98"', '74H-93.98'),
    ('2380.95', '75H-95.24"', '75H-95.24'),
    ('2412.95', '76H-96.50"', '76H-96.5')
    ]

END_CONDITIONS = [
    ('EP', 'End Panel', 'EP (Panel Visible)'),
    ('WP', 'Wall Panel', 'WP (Panel Against Wall)'),
    ('CP', 'Center Panel', 'CP (Panel Against Panel)'),
    ('OFF', 'Off', 'Turn Off Side')
    ]

DRAWER_SIZES_DICT = {
    '91.948': '3 H',
    '91.95': '3 H',
    '123.952': '4 H',
    '123.95': '4 H',
    '155.956': '5 H',
    '155.95': '5 H',
    '187.96': '6 H',
    '187.95': '6 H',
    '219.95': '7 H',
    '219.964': '7 H',
    '251.968': '8 H',
    '251.95': '8 H',
    '283.972': '9 H',
    '283.95': '9 H',
    '315.976': '10 H',
    '315.95': '10 H',
    '347.98': '11 H',
    '347.95': '11 H',
    '379.95': '12 H',
    '379.984': '12 H'
}

FIVE_HOLE_FRONT_HEIGHTS = [
    ('155.956', '5H-6.14"', '5H-6.14"'),
    ('187.96', '6H-7.40"', '6H-7.40"'),
    ('219.964', '7H-8.66"', '7H-8.66"'),
    ('251.968', '8H-9.92"', '8H-9.92"'),
    ('283.972', '9H-11.18"', '9H-11.18"'),
    ('315.976', '10H-12.44"', '10H-12.44"'),
    ('347.98', '11H-13.70"', '11H-13.70"'),
    ('379.984', '12H-14.96"', '12H-14.96"')
    ]

SIX_HOLE_FRONT_HEIGHTS = [
    ('187.96', '6H-7.40"', '6H-7.40"'),
    ('219.964', '7H-8.66"', '7H-8.66"'),
    ('251.968', '8H-9.92"', '8H-9.92"'),
    ('283.972', '9H-11.18"', '9H-11.18"'),
    ('315.976', '10H-12.44"', '10H-12.44"'),
    ('347.98', '11H-13.70"', '11H-13.70"'),
    ('379.984', '12H-14.96"', '12H-14.96"')
    ]

EIGHT_HOLE_FRONT_HEIGHTS = [
    ('251.968', '8H-9.92"', '8H-9.92"'),
    ('283.972', '9H-11.18"', '9H-11.18"'),
    ('315.976', '10H-12.44"', '10H-12.44"'),
    ('347.98', '11H-13.70"', '11H-13.70"'),
    ('379.984', '12H-14.96"', '12H-14.96"')
    ]

FIVE_HOLE_DRAWER_STYLE_LIST = [
    'Pisa',
    'Verona',
    'Volterra',
    'Carrara',
    'Portofino',
    'Napoli',
    'Merano',
    'Milano',
    'Venice',
    'Siena',
    'San Marino',
    'Capri',
    'Moderno'
]

SIX_HOLE_DRAWER_STYLE_LIST = [
    'Aviano',
    'Florence',
    'Colina',
    'Rome',
    'Bergamo',
    'Palermo',
    'Molino Vecchio',
    'Traviso'
]

EIGHT_HOLE_DRAWER_STYLE_LIST = [
    'Miramare'
]

HAMPER_SIZES_DICT = {
    '557.276': '18 H',
    '589.28': '19 H',
    '621.284': '20 H',
    '653.288': '21 H',
    '685.292': '22 H'
}

DOOR_SIZES_DICT = {
    '3.62': '3 H',
    '4.88': '4 H',
    '6.14': '5 H',
    '7.4': '6 H',
    '8.66': '7 H',
    '9.92': '8 H',
    '11.18': '9 H',
    '12.44': '10 H',
    '13.7': '11 H',
    '14.96': '12 H',
    '16.22': '13 H',
    '17.48': '14 H',
    '18.74': '15 H',
    '20': '16 H',
    '21.26': '17 H',
    '22.52': '18 H',
    '23.78': '19 H',
    '25.04': '20 H',
    '26.3': '21 H',
    '27.56': '22 H',
    '28.82': '23 H',
    '30.08': '24 H',
    '31.34': '25 H',
    '32.6': '26 H',
    '33.86': '27 H',
    '35.12': '28 H',
    '36.38': '29 H',
    '37.64': '30 H',
    '38.9': '31 H',
    '40.16': '32 H',
    '41.42': '33 H',
    '42.68': '34 H',
    '43.94': '35 H',
    '45.2': '36 H',
    '46.46': '37 H',
    '47.72': '38 H',
    '48.98': '39 H',
    '50.24': '40 H',
    '51.5': '41 H',
    '53.66': '42 H',
    '54.02': '43 H',
    '55.28': '44 H',
    '56.54': '45 H',
    '57.8': '46 H',
    '59.06': '47 H',
    '60.31': '48 H',
    '61.57': '49 H',
    '62.83': '50 H',
    '64.09': '51 H',
    '65.35': '52 H',
    '66.61': '53 H',
    '67.87': '54 H',
    '69.13': '55 H',
    '70.39': '56 H',
    '71.65': '57 H',
    '72.91': '58 H',
    '74.17': '59 H',
    '75.43': '60 H',
    '76.69': '61 H',
    '77.95': '62 H',
    '79.21': '63 H',
    '80.47': '64 H',
    '81.73': '65 H',
    '82.99': '66 H',
    '84.25': '67 H',
    '85.51': '68 H',
    '86.77': '69 H',
    '88.03': '70 H',
    '89.29': '71 H',
    '90.55': '72 H',
    '91.82': '73 H',
    '93.07': '74 H',
    '94.33': '75 H',
    '95.59': '76 H'
}

JEWELRY_INSERTS_18IN_LIST = [
    'Jewelry Insert Black',
    'Jewelry Insert Maroon',
    'Jewelry Insert Sterling Grey',
    'Velvet Liner Black',
    'Velvet Liner Maroon',
    'Velvet Liner Sterling Grey'
]

JEWELRY_INSERTS_21IN_LIST = [
    'Jewelry Insert Black',
    'Jewelry Insert Clear',
    'Jewelry Insert Maroon',
    'Jewelry Insert Sterling Grey',
    'Velvet Liner Black',
    'Velvet Liner Maroon',
    'Velvet Liner Sterling Grey'
]

JEWELRY_INSERTS_24IN_LIST = [
    'Jewelry Insert Black',
    'Jewelry Insert Clear',
    'Jewelry Insert Maroon',
    'Jewelry Insert Sterling Grey',
    'Velvet Liner Black',
    'Velvet Liner Maroon',
    'Velvet Liner Sterling Grey'
]

JEWELRY_INSERTS_VELVET_LINERS_18IN_LIST = [
    'None',
    'Jewelry Insert Black',
    'Jewelry Insert Maroon',
    'Jewelry Insert Sterling Grey',
    'Velvet Liner Black',
    'Velvet Liner Maroon',
    'Velvet Liner Sterling Grey'
]

JEWELRY_INSERTS_VELVET_LINERS_21IN_LIST = [
    'None',
    'Jewelry Insert Black',
    'Jewelry Insert Clear',
    'Jewelry Insert Maroon',
    'Jewelry Insert Sterling Grey',
    'Velvet Liner Black',
    'Velvet Liner Maroon',
    'Velvet Liner Sterling Grey'
]

JEWELRY_INSERTS_VELVET_LINERS_24IN_LIST = [
    'None',
    'Jewelry Insert Black',
    'Jewelry Insert Clear',
    'Jewelry Insert Maroon',
    'Jewelry Insert Sterling Grey',
    'Velvet Liner Black',
    'Velvet Liner Maroon',
    'Velvet Liner Sterling Grey'
]

SLIDING_INSERTS_18IN_LIST = [
    'Sliding Insert Black',
    'Sliding Insert Maroon',
    'Sliding Insert Sterling Grey'
]

SLIDING_INSERTS_21IN_LIST = [
    'Sliding Insert Black',
    'Sliding Insert Maroon',
    'Sliding Insert Sterling Grey'
]

SLIDING_INSERTS_24IN_LIST = [
    'Sliding Insert Black',
    'Sliding Insert Maroon',
    'Sliding Insert Sterling Grey'
]

VELVET_LINERS_LIST = [
    'Velvet Liner Black',
    'Velvet Liner Maroon',
    'Velvet Liner Sterling Grey'
]

PLACEMENT_X = ['Left', 'Right']

PLACEMENT_Y = ['Front', 'Back']

JEWELRY_TYPE_LIST = [
    'Double Jewelry', 
    'Std Opening', 
    'Non Std Opening GT 16', 
    'Non Std Opening LT 16'
]

JEWELRY_INSERTS_18IN_OPTIONS = [
    ('0', 'Jewelry Insert Black', 'Jewelry Insert Black'),
    ('1', 'Jewelry Insert Maroon', 'Jewelry Insert Maroon'),
    ('2', 'Jewelry Insert Sterling Grey', 'Jewelry Insert Sterling Grey'),
    ('3', 'Velvet Liner Black', 'Velvet Liner Black'),
    ('4', 'Velvet Liner Maroon', 'Velvet Liner Maroon'),
    ('5', 'Velvet Liner Sterling Grey', 'Velvet Liner Sterling Grey')
]

JEWELRY_INSERTS_21IN_OPTIONS = [
    ('0', 'Jewelry Insert Black', 'Jewelry Insert Black'),
    ('1', 'Jewelry Insert Clear', 'Jewelry Insert Clear'),
    ('2', 'Jewelry Insert Maroon', 'Jewelry Insert Maroon'),
    ('3', 'Jewelry Insert Sterling Grey', 'Jewelry Insert Sterling Grey'),
    ('4', 'Velvet Liner Black', 'Velvet Liner Black'),
    ('5', 'Velvet Liner Maroon', 'Velvet Liner Maroon'),
    ('6', 'Velvet Liner Sterling Grey', 'Velvet Liner Sterling Grey')
]

JEWELRY_INSERTS_24IN_OPTIONS = [
    ('0', 'Jewelry Insert Black', 'Jewelry Insert Black'),
    ('1', 'Jewelry Insert Clear', 'Jewelry Insert Clear'),
    ('2', 'Jewelry Insert Maroon', 'Jewelry Insert Maroon'),
    ('3', 'Jewelry Insert Sterling Grey', 'Jewelry Insert Sterling Grey'),
    ('4', 'Velvet Liner Black', 'Velvet Liner Black'),
    ('5', 'Velvet Liner Maroon', 'Velvet Liner Maroon'),
    ('6', 'Velvet Liner Sterling Grey', 'Velvet Liner Sterling Grey')
]

JEWELRY_INSERTS_VELVET_LINERS_18IN_OPTIONS = [
    ('0', 'None', 'None'),
    ('1', 'Jewelry Insert Black', 'Jewelry Insert Black'),
    ('2', 'Jewelry Insert Maroon', 'Jewelry Insert Maroon'),
    ('3', 'Jewelry Insert Sterling Grey', 'Jewelry Insert Sterling Grey'),
    ('4', 'Velvet Liner Black', 'Velvet Liner Black'),
    ('5', 'Velvet Liner Maroon', 'Velvet Liner Maroon'),
    ('6', 'Velvet Liner Sterling Grey', 'Velvet Liner Sterling Grey')
]

JEWELRY_INSERTS_VELVET_LINERS_21IN_OPTIONS = [
    ('0', 'None', 'None'),
    ('1', 'Jewelry Insert Black', 'Jewelry Insert Black'),
    ('2', 'Jewelry Insert Clear', 'Jewelry Insert Clear'),
    ('3', 'Jewelry Insert Maroon', 'Jewelry Insert Maroon'),
    ('4', 'Jewelry Insert Sterling Grey', 'Jewelry Insert Sterling Grey'),
    ('5', 'Velvet Liner Black', 'Velvet Liner Black'),
    ('6', 'Velvet Liner Maroon', 'Velvet Liner Maroon'),
    ('7', 'Velvet Liner Sterling Grey', 'Velvet Liner Sterling Grey')
]

JEWELRY_INSERTS_VELVET_LINERS_24IN_OPTIONS = [
    ('0', 'None', 'None'),
    ('1', 'Jewelry Insert Black', 'Jewelry Insert Black'),
    ('2', 'Jewelry Insert Clear', 'Jewelry Insert Clear'),
    ('3', 'Jewelry Insert Maroon', 'Jewelry Insert Maroon'),
    ('4', 'Jewelry Insert Sterling Grey', 'Jewelry Insert Sterling Grey'),
    ('5', 'Velvet Liner Black', 'Velvet Liner Black'),
    ('6', 'Velvet Liner Maroon', 'Velvet Liner Maroon'),
    ('7', 'Velvet Liner Sterling Grey', 'Velvet Liner Sterling Grey')
]

SLIDING_INSERTS_18IN_OPTIONS = [
    ('0', 'Sliding Insert Black', 'Sliding Insert Black'),
    ('1', 'Sliding Insert Maroon', 'Sliding Insert Maroon'),
    ('2', 'Sliding Insert Sterling Grey', 'Sliding Insert Sterling Grey')
]

SLIDING_INSERTS_21IN_OPTIONS = [
    ('0', 'Sliding Insert Black', 'Sliding Insert Black'),
    ('1', 'Sliding Insert Maroon', 'Sliding Insert Maroon'),
    ('2', 'Sliding Insert Sterling Grey', 'Sliding Insert Sterling Grey')
]

SLIDING_INSERTS_24IN_OPTIONS = [
    ('0', 'Sliding Insert Black', 'Sliding Insert Black'),
    ('1', 'Sliding Insert Maroon', 'Sliding Insert Maroon'),
    ('2', 'Sliding Insert Sterling Grey', 'Sliding Insert Sterling Grey')
]

VELVET_LINERS_OPTIONS = [
    ('0', 'Velvet Liner Black', 'Velvet Liner Black'),
    ('1', 'Velvet Liner Maroon', 'Velvet Liner Maroon'),
    ('2', 'Velvet Liner Sterling Grey', 'Velvet Liner Sterling Grey')
]

JEWELRY_TYPE_OPTIONS = [
    ('0', 'Double Jewelry', 'Double Jewelry'),
    ('1', 'Std Opening', 'Std Opening'),
    ('2', 'Non Std Opening GT 16', 'Non Std Opening GT 16'),
    ('3', 'Non Std Opening LT 16', 'Non Std Opening LT 16')
]

PLACEMENT_OPTIONS_X = [('0','Left', 'Left'), 
                       ('1', 'Right', 'Right')]

PLACEMENT_OPTIONS_Y = [('0','Front', 'Front'), 
                       ('1', 'Back', 'Back')]

JEWELRY_INSERTS_18IN_DICT = {
    0: 'Jewelry 18in Black',
    1: 'Jewelry 18in Maroon',
    2: 'Jewelry 18in Sterling Grey',
    3: 'Velvet Liner - Black',
    4: 'Velvet Liner - Burgundy',
    5: 'Velvet Liner - Sterling Grey'
}

JEWELRY_INSERTS_21IN_DICT = {
    0: 'Jewelry 21in Black',
    1: 'Jewelry 21in Lucite',
    2: 'Jewelry 21in Maroon',
    3: 'Jewelry 21in Sterling Grey',
    4: 'Velvet Liner - Black',
    5: 'Velvet Liner - Burgundy',
    6: 'Velvet Liner - Sterling Grey'
}

JEWELRY_INSERTS_24IN_DICT = {
    0: 'Jewelry 24in Black',
    1: 'Jewelry 24in Lucite',
    2: 'Jewelry 24in Maroon',
    3: 'Jewelry 24in Sterling Grey',
    4: 'Velvet Liner - Black',
    5: 'Velvet Liner - Burgundy',
    6: 'Velvet Liner - Sterling Grey'
}

JEWELRY_INSERTS_VELVET_LINERS_18IN_DICT = {
    0: 'None',
    1: 'Jewelry 18in Black',
    2: 'Jewelry 18in Maroon',
    3: 'Jewelry 18in Sterling Grey',
    4: 'Velvet Liner - Black',
    5: 'Velvet Liner - Burgundy',
    6: 'Velvet Liner - Sterling Grey'
}

JEWELRY_INSERTS_VELVET_LINERS_21IN_DICT = {
    0: 'None',
    1: 'Jewelry 21in Black',
    2: 'Jewelry 21in Lucite',
    3: 'Jewelry 21in Maroon',
    4: 'Jewelry 21in Sterling Grey',
    5: 'Velvet Liner - Black',
    6: 'Velvet Liner - Burgundy',
    7: 'Velvet Liner - Sterling Grey'
}

JEWELRY_INSERTS_VELVET_LINERS_24IN_DICT = {
    0: 'None',
    1: 'Jewelry 24in Black',
    2: 'Jewelry 24in Lucite',
    3: 'Jewelry 24in Maroon',
    4: 'Jewelry 24in Sterling Grey',
    5: 'Velvet Liner - Black',
    6: 'Velvet Liner - Burgundy',
    7: 'Velvet Liner - Sterling Grey'
}

VELVET_LINERS_DICT = {
    0: 'Velvet Liner - Black',
    1: 'Velvet Liner - Burgundy',
    2: 'Velvet Liner - Sterling Grey'
}

EMPTY_PDF_FIELDS = {
    "ext_color": "",
    "int_color": "",
    "trim_color": "",
    "veneer": "",
    "full_backs": "",
    "edge": "",
    "edge_dolce": "",
    "edge_3m_pvc": "",
    "door_mel_qty": "",
    "door_mel": "",
    "wood_door_qty": "",
    "wood_door": "",
    "glass_inset_qty": "",
    "glass_inset": "",
    "lucite_qty": "",
    "lucite": "",
    "hinge_qty": "",
    "hinge": "",
    "door_hardware_qty": "",
    "door_hardware": "",
    "more_door_hardware_qty": "",
    "more_door_hardware": "",
    "hamper_face_qty": "",
    "hamper_face": "",
    "hamper_hardware_qty": "",
    "hamper_hardware": "",
    "drawer_boxes_qty": "",
    "drawer_boxes": "",
    "drawer_slides_qty": "",
    "drawer_slides": "",
    "drawer_mel_qty": "",
    "drawer_mel": "",
    "wood_drawer_qty": "",
    "wood_drawer": "",
    "file_rails_qty": "",
    "file_rails": "",
    "drawer_hardware_qty": "",
    "drawer_hardware": "",
    "more_drawer_hardware_qty": "",
    "more_drawer_hardware": "",
    "jewelry_qty": "",
    "jewelry": "",
    "sld_tray_qty": "",
    "sld_tray": "",
    "vel_bottom_qty": "",
    "vel_bottom": "",
    "hamper_qty": "",
    "hamper": "",
    "hamper_bag_qty": "",
    "hamper_bag": "",
    "rod_qty": "",
    "rod_style": "",
    "handiwall_qty": "",
    "handiwall": "",
    "reach_pole_qty": "",
    "reach_pole": "",
    "belt_rack_qty": "",
    "belt_rack_style": "",
    "tie_rack_qty": "",
    "tie_rack_style": "",
    "valet_qty": "",
    "valet_style": "",
    "legs_qty": "",
    "legs": "",
    "hooks_qty": "",
    "hooks_style": "",
    "misc_qty": "",
    "misc_style": "",
    "ct_type": "",
    "ct_color": "",
    "ct_chip": "",
    "ct_client": "",
    "tear_out": "",
    "block_wall": "",
    "elevator": "",
    "touch_up": "",
    "new_construction": "",
    "stairs": "",
    "floor_type": "",
    "door_type": "",
    "basebrd": "",
    "parking": "",
    "proj_notes": "",
    "signature": "",
    "job_number": "",
    "install_date": "",
    "sheet": "",
    "customer_name": "",
    "lead_id": "",
    "cphone": "",
    "design_date": "",
    "designer": ""
}

FULLBACK_LABEL_OPTIONS = {
    0: 'FB|1/4"', 
    1: 'FB|3/4"', 
    2: 'FB|Cedar'
}