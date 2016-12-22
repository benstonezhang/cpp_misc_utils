//
// Created by Benstone on 16/12/21.
//

#ifndef WGS_UTILS_H
#define WGS_UTILS_H

int wgs_in_prc(const double lat, const double lng);
void wgs_wgs84_to_gcj02(const double lat, const double lng, double *mlat, double *mlng);
void wgs_gcj02_to_wgs84(const double mlat, const double mlng, double *lat, double *lng);
void wgs_gcj02_to_bd09(const double mlat, const double mlng, double *blat, double *blng);
void wgs_bd09_to_gcj02(const double blat, const double blng, double *mlat, double *mlng);

#endif //WGS_UTILS_H
