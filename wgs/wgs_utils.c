//
// Created by Benstone on 16/12/21.
//

#include <math.h>
#include "wgs_utils.h"

static const double radian_per_degree = M_PI / 180.0;
static const double radian_of_degree_3000  = M_PI * 3000.0 / 180.0;

/*
 * Krasovsky 1940 (SK-42):
 *   a = 6378245.0, 1/f = 298.3, b = a * (1 - f)
 *   ee = (a^2 - b^2) / a^2
 */
static const double gcj02_a = 6378245.0;                // 长半轴
static const double gcj02_ee = 0.00669342162296594323;  // 扁率

static const double china_center_latitude = 35.0;
static const double china_center_longitude = 105.0;
static const double china_longitude_min = 72.004;
static const double china_longitude_max = 137.8347;
static const double china_latitude_min = 0.8293;
static const double china_latitude_max = 55.8271;

#ifdef WGS_UTILS_TEST

#include <stdio.h>

int main(int argc, char **argv)
{
	double lat = 37.065;
	double lng = 128.543;
	double a, b;
	printf("Input: (%.16f, %.16f)\n", lat, lng);
	puts("Reference:\n"
		 "  WGS84 -> GCJ02: [37.065651049489816, 128.54820547949757]\n"
		 "  GCJ02 -> WGS84: [37.06434895051018,  128.53779452050244]\n"
		 "  GCJ02 -> BD09:  [37.07113427883019,  128.54944656269413]\n"
		 "  BD09  -> GCJ02: [37.07113427883019,  128.5365893261212]\n"
		 "Output:");
	wgs_wgs84_to_gcj02(lat,lng, &a, &b);
	printf("  WGS84 -> GCJ02: (%.16f, %.16f)\n", a, b);
	wgs_gcj02_to_wgs84(lat,lng, &a, &b);
	printf("  GCJ02 -> WGS84: (%.16f, %.16f)\n", a, b);
	wgs_gcj02_to_bd09(lat,lng, &a, &b);
	printf("  GCJ02 -> BD09:  (%.16f, %.16f)\n", a, b);
	wgs_bd09_to_gcj02(lat,lng, &a, &b);
	printf("  BD09  -> GCJ02: (%.16f, %.16f)\n", a, b);
	return 0;
}

#endif

static void wgs_gcj02_transform(const double lat, const double lng, double *dlat, double *dlng)
{
	const double lng_pi = lng * M_PI;
	const double lat_pi = lat * M_PI;
	const double lng_times_lat = lng * lat;
	*dlat = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng_times_lat + 0.2 * sqrt(fabs(lng)) +
			40.0 * (sin(6.0 * lng_pi) + sin(2.0 * lng_pi) + sin(lat_pi) + 2.0 * sin(lat_pi / 3.0) +
					8.0 * sin(lat_pi / 12.0) + 16.0 * sin(lat_pi / 30.0)) / 3.0;
	*dlng = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng_times_lat + 0.1 * sqrt(fabs(lng)) +
			40.0 * (sin(6.0 * lng_pi) + sin(2.0 * lng_pi) + sin(lng_pi) + 2.0 * sin(lng_pi / 3.0)) / 3.0 +
	        100.0 * sin(lng_pi / 12.0) + 200.0 * sin(lng_pi / 30.0);
}

static void wgs_gcj02_offset(const double lat, const double lng, double *lat_offset, double *lng_offset)
{
	double dlat, dlng;
	wgs_gcj02_transform(lat - china_center_latitude, lng - china_center_longitude, &dlat, &dlng);
	const double radlat = lat * radian_per_degree;
	const double sin_radlat = sin(radlat);
	const double magic = 1 - gcj02_ee * sin_radlat * sin_radlat;
	const double sqrtmagic = sqrt(magic);
	*lat_offset = (dlat * magic * sqrtmagic) / (gcj02_a * (1 - gcj02_ee) * radian_per_degree);
	*lng_offset = (dlng * sqrtmagic) / (gcj02_a * cos(radlat) * radian_per_degree);
//	printf("%.16f, %.16f, %.16f, %.16f\n", radlat, sin_radlat, magic, sqrtmagic);
//	printf("[%.16f, %.16f] -> [%.16f, %.16f], [%.16f, %.16f]\n", lat, lng, dlat, dlng, *lat_offset, *lng_offset);
}

int wgs_in_prc(const double lat, const double lng)
{
	if ((lng > china_longitude_min) && (lng < china_longitude_max) &&
		(lat > china_latitude_min) && (lat < china_latitude_max)) {
		return 1;
	} else {
		return 0;
	}
}

void wgs_wgs84_to_gcj02(const double lat, const double lng, double *mlat, double *mlng)
{
	double dlat, dlng;
	wgs_gcj02_offset(lat, lng, &dlat, &dlng);
	*mlat = lat + dlat;
	*mlng = lng + dlng;
}

void wgs_gcj02_to_wgs84(const double mlat, const double mlng, double *lat, double *lng)
{
	double dlat, dlng;
	wgs_gcj02_offset(mlat, mlng, &dlat, &dlng);
	*lat = mlat - dlat;
	*lng = mlng - dlng;
}

void wgs_gcj02_to_bd09(const double mlat, const double mlng, double *blat, double *blng)
{
	const double z = sqrt(mlng * mlng + mlat * mlat) + 0.00002 * sin(mlat * radian_of_degree_3000);
	const double theta = atan2(mlat, mlng) + 0.000003 * cos(mlng * radian_of_degree_3000);
	*blat = z * sin(theta) + 0.006;
	*blng = z * cos(theta) + 0.0065;
}

void wgs_bd09_to_gcj02(const double blat, const double blng, double *mlat, double *mlng)
{
	const double x = blng - 0.0065;
	const double y = blat - 0.006;
	const double z = sqrt(x * x + y * y) - 0.00002 * sin(y * radian_of_degree_3000);
	const double theta = atan2(y, x) - 0.000003 * cos(x * radian_of_degree_3000);
	*mlat = z * sin(theta);
	*mlng = z * cos(theta);
}
