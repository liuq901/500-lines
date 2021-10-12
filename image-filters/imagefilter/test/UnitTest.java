package imagefilter.test;

import org.junit.internal.TextListener;
import org.junit.runner.JUnitCore;

import org.junit.internal.RealSystem;

import imagefilter.color.ColorHelperTest;
import imagefilter.model.ImageStateTest;

public class UnitTest
{
    JUnitCore junit;

    public UnitTest()
    {
        junit = new JUnitCore();
        junit.addListener(new TextListener(System.out));
    }

    public void test()
    {
        test(ColorHelperTest.class);
        test(ImageStateTest.class);
    }

    private void test(Class testClass)
    {
        if (!junit.run(testClass).wasSuccessful())
            throw new RuntimeException("Failed test on " + testClass.getSimpleName());
    }
}

