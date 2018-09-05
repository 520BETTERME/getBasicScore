package cn.betterme.BasicScore;
/*
 *Author: BETTER ME   Date: 2018/9/5   Time: 14:48
 */
import org.dom4j.Document;
import org.dom4j.DocumentException;
import org.dom4j.Element;
import org.dom4j.io.SAXReader;

import java.util.ArrayList;
import java.util.List;

public class GetBasicScore {

    private final double C_C_PERC = 0.7;    //必修课百分比
    private final double E_C_PERC = 0.3;    //选修课百分比
    private final double A_C_PERC = 0.9;    //所有课程百分比

    private double CCCredits = 0;    //必修课总学分
    private double ECCredits = 0;    //选修课总学分


    private Document getDocument() throws DocumentException {

        SAXReader saxReader = new SAXReader();
        Document document = saxReader.read("scoreConfig.xml");
        Element root = document.getRootElement();
//        CCCredits = Double.parseDouble(root.element("total-credits-for-compulsory-courses").getText());
//        ECCredits = Double.parseDouble(root.element("total-credits-for-elective-courses").getText());
        return document;
    }

    private List<Course> getCourses(int attribute) throws DocumentException {

        Document document = getDocument();
//        String xpanth = "//" + ACCOUNT_INFO_ELEMENTS + "[@id='" + id + "']";
        String xpath = "//courses" + "[@attribute='" + attribute +"']";
        List<Element> courseELes = document.selectNodes(xpath);
        List<Course> courses = new ArrayList<Course>();
        for (Element ele: courseELes) {
            courses.add(new Course(Double.parseDouble(ele.elementText("credit")), Integer.parseInt(ele.elementText("score"))));
        }
        return courses;
    }

    public double getBasicScore() {

        Double basicScore = 0.0;
        try {
            //得到必修课
            List<Course> CCourses = getCourses(1);
            //得到选修课
            List<Course> ECourses = getCourses(2);

            Double CCoursesScore = 0.0; //必修课总成绩（成绩*学分之和）
            Double ECoursesScore = 0.0; //选修课总成绩（成绩*学分之和）

            for (Course c: CCourses) {
                CCoursesScore += c.getScore() * c.getCredit();
                CCCredits += c.getCredit();

            }
            //System.out.println("CCC" + CCCredits);

            for (Course c: ECourses) {
                ECoursesScore += c.getScore() * c.getCredit();
                ECCredits += c.getCredit();

            }
            //System.out.println("ECC" + ECCredits);

            //（必修课总成绩/必修课总学分 * 0.7 + 选修课总成绩/选修课总学分 * 0.3）*0.9
            basicScore = (CCoursesScore/CCCredits * C_C_PERC + ECoursesScore/ECCredits * E_C_PERC) * A_C_PERC;

        }catch (Exception e) {
            e.printStackTrace();
        }
        return basicScore;
    }

}
