using System;
using System.Windows.Forms;

namespace SmartGrid.WinFormsClient;

public class Program
{
    [STAThread]
    public static void Main(string[] args)
    {
        Application.EnableVisualStyles();
        Application.Run(new MainForm());
    }
}

public class MainForm : Form
{
    public MainForm()
    {
        Text = "Smart Grid Console";
    }
}
