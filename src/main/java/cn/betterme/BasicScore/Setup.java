package cn.betterme.BasicScore;
/*
 *Author: BETTER ME   Date: 2018/9/5   Time: 16:23
 */

import java.io.File;
import java.io.FileWriter;

public class Setup {
    public static void main(String[] args){

        Double score = new GetBasicScore().getBasicScore();
        //System.out.println(score);
        File file = new File("result.txt");
        try {
            FileWriter fw = new FileWriter(file);
            fw.write(String.valueOf(score));
            fw.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

    }
}
