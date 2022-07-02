package com.ymlai87416.stockoption.server.utilities;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 * Created by Tom on 6/10/2016.
 */
public class Utilities {

    public static java.util.Date convertSQLDateToUtilDate(java.sql.Date sqlDate){
        java.util.Date utilDate = new java.util.Date(sqlDate.getTime());
        return utilDate;
    }

    public static java.sql.Date convertUtilDateToSqlDate(java.util.Date utilDate){
        java.sql.Date sqlDate = new java.sql.Date(utilDate.getTime());
        return sqlDate;
    }

    public static java.sql.Date getCurrentSQLDateTime(){
        return convertUtilDateToSqlDate(new java.util.Date());
    }

    public static java.sql.Date getCurrentSQLDate(){
        java.util.Date currentTime = new java.util.Date();
        java.util.Date today = new java.util.Date(currentTime.getYear(), currentTime.getMonth(), currentTime.getDate());

        return convertUtilDateToSqlDate(today);
    }

    public static java.util.Date getNextDate(java.util.Date date){
        Calendar cal = Calendar.getInstance();
        cal.setTime(date);
        cal.add( Calendar.DATE, 1 );
        return cal.getTime();
    }

    private static SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");

    public static Date[] parseStartDateAndEndDate(String startDate, String endDate){
        Date[] result = new Date[2];
        try {
            if (startDate != null) {
                result[0] = sdf.parse(startDate);
                if (endDate == null) {
                    Calendar cal = Calendar.getInstance();
                    cal.setTime(result[0]);
                    cal.add(Calendar.DATE, 0);
                    result[1] = cal.getTime();
                }
                else
                    result[1] = sdf.parse(endDate);
            }

            return result;
        } catch (Exception ex) {
            return new Date[0];
        }
    }
}
