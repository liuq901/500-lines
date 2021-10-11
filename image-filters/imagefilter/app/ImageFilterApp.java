package imagefilter.app;

import java.io.File;

import processing.core.PApplet;

import imagefilter.color.ColorHelper;
import imagefilter.color.PixelColorHelper;
import imagefilter.model.ImageState;

@SuppressWarnings("serial")
public class ImageFilterApp extends PApplet
{
    static final String INSTRUCTIONS = ""
        + "R: increase red filter\nE: reduce red filter\n"
        + "G: increase green filter\nF: reduce green filter\n"
        + "B: increase blue filter\nV: reduce blue filter\n"
        + "I: increase hue tolerance\nU: reduce hue tolerance\n"
        + "S: show dominant hue\nH: hide dominant hue\n"
        + "P: process image\nC: choose a new file\n"
        + "W: save file\nSPACE: reset image\n";

    static final int FILTER_HEIGHT = 2;
    static final int FILTER_INCREMENT = 5;
    static final int HUE_INCREMENT = 2;
    static final int HUE_RANGE = 100;
    static final int IMAGE_MAX = 640;
    static final int RGB_COLOR_RANGE = 100;
    static final int SIDE_BAR_PADDING = 10;
    static final int SIDE_BAR_WIDTH = RGB_COLOR_RANGE + 2 * SIDE_BAR_PADDING + 50;

    private ImageState imageState;

    boolean redrawImage = true;

    public static void main(String[] args)
    {
        PApplet.main("imagefilter.app.ImageState");
    }

    @Override
    public void setup()
    {
        noLoop();
        imageState = new ImageState(new ColorHelper(new PixelColorHelper()));

        size(IMAGE_MAX + SIDE_BAR_PADDING, IMAGE_MAX);
        background(0);

        chooseFile();
    }

    @Override
    public void draw()
    {
        if (imageState.image().image() != null && redrawImage)
        {
            background(0);
            drawImage();
        }

        colorMode(RGB, RGB_COLOR_RANGE);
        fill(0);
        rect(IMAGE_MAX, 0, SIDE_BAR_WIDTH, IMAGE_MAX);
        stroke(RGB_COLOR_RANGE);
        line(IMAGE_MAX, 0, IMAGE_MAX, IMAGE_MAX);

        int x = IMAGE_MAX + SIDE_BAR_PADDING;
        int y = 2 * SIDE_BAR_PADDING;
        stroke(RGB_COLOR_RANGE, 0, 0);
        line(x, y, x + RGB_COLOR_RANGE, y);
        line(x + imageState.redFilter(), y - FILTER_HEIGHT, x + imageState.redFilter(), y + FILTER_HEIGHT);

        y += 2 * SIDE_BAR_PADDING;
        stroke(0, RGB_COLOR_RANGE, 0);
        line(x, y, x + RGB_COLOR_RANGE, y);
        line(x + imageState.greenFilter(), y - FILTER_HEIGHT, x + imageState.greenFilter(), y + FILTER_HEIGHT);

        y += 2 * SIDE_BAR_PADDING;
        stroke(0, 0, RGB_COLOR_RANGE);
        line(x, y, x + RGB_COLOR_RANGE, y);
        line(x + imageState.blueFilter(), y - FILTER_HEIGHT, x + imageState.blueFilter(), y + FILTER_HEIGHT);

        y += 2 * SIDE_BAR_PADDING;
        stroke(HUE_RANGE);
        line(x, y, x + HUE_RANGE, y);
        line(x + imageState.hueTolerance(), y - FILTER_HEIGHT, x + imageState.hueTolerance(), y + FILTER_HEIGHT);

        y += 4 * SIDE_BAR_PADDING;
        fill(RGB_COLOR_RANGE);
        text(INSTRUCTIONS, x, y);

        updatePixels();
    }

    public void fileSelected(File file)
    {
        if (file == null)
            println("User hit cancel.");
        else
        {
            imageState.setFilepath(file.getAbsolutePath());
            imageState.setUpImage(this, IMAGE_MAX);
            redrawImage = true;
            redraw();
        }
    }

    private void drawImage()
    {
        imageMode(CENTER);
        imageState.updateImage(this, HUE_RANGE, RGB_COLOR_RANGE, IMAGE_MAX);
        int width = imageState.image().getWidth();
        int height = imageState.image().getHeight();
        image(imageState.image().image(), IMAGE_MAX / 2, IMAGE_MAX / 2, width, height);
        redrawImage = false;
    }

    @Override
    public void keyPressed()
    {
        switch (key)
        {
            case 'c':
                chooseFile();
                break;
            case 'p':
                redrawImage = true;
                break;
            case ' ':
                imageState.resetImage(this, IMAGE_MAX);
                redrawImage = true;
                break;
        }
        imageState.processKeyPress(key, FILTER_INCREMENT, RGB_COLOR_RANGE, HUE_INCREMENT, HUE_RANGE);
        redraw();
    }

    private void chooseFile()
    {
        selectInput("Select a file to process:", "fileSelected");
    }
}

