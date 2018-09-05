package cn.betterme.BasicScore;
/*
 *Author: BETTER ME   Date: 2018/9/5   Time: 14:49
 */

public class Course {

    private String name;    //课程名
    private int attribute;  //课程属性，1为必修课2为选修课
    private double credit;  //学分
    private int score;  //分数

    public Course(double credit, int score) {
        this.credit = credit;
        this.score = score;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAttribute() {
        return attribute;
    }

    public void setAttribute(int attribute) {
        this.attribute = attribute;
    }

    public double getCredit() {
        return credit;
    }

    public void setCredit(double credit) {
        this.credit = credit;
    }

    public int getScore() {
        return score;
    }

    public void setScore(int score) {
        this.score = score;
    }
}
