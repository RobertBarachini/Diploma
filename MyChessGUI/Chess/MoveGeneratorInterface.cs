using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

public class MoveGeneratorInterface
{
    private Process moveGeneratorProcess;
    private StreamWriter processInput;
    private StringBuilder processOutput;
    private string processOutputLastLine;
    private StringBuilder processError;
    private string generatorFilename = "stockfish_10_x64.exe";

    public MoveGeneratorInterface()
    {
        Init();
    }

    private void Init()
    {
        moveGeneratorProcess = new Process();
        moveGeneratorProcess.StartInfo.FileName = Path.Combine(Directory.GetCurrentDirectory(), generatorFilename);
        moveGeneratorProcess.StartInfo.Arguments = "";
        moveGeneratorProcess.StartInfo.CreateNoWindow = true;
        moveGeneratorProcess.StartInfo.UseShellExecute = false;
        moveGeneratorProcess.StartInfo.RedirectStandardOutput = true;
        moveGeneratorProcess.StartInfo.RedirectStandardError = true;
        moveGeneratorProcess.StartInfo.RedirectStandardInput = true;
        moveGeneratorProcess.OutputDataReceived += MoveGeneratorProcess_OutputDataReceived;
        moveGeneratorProcess.ErrorDataReceived += MoveGeneratorProcess_ErrorDataReceived;
        moveGeneratorProcess.EnableRaisingEvents = true;
        moveGeneratorProcess.Exited += MoveGeneratorProcess_Exited;
        moveGeneratorProcess.Start();
        moveGeneratorProcess.BeginOutputReadLine();
        moveGeneratorProcess.BeginErrorReadLine();

        processOutput = new StringBuilder();
        processError = new StringBuilder();
        processOutputLastLine = "";
        processInput = moveGeneratorProcess.StandardInput;
        //processInput.WriteLine("d");
        processInput.WriteLine("setoption name MultiPV value 500"); // 500 is upper bound

        //getMoves("");
    }

    private void MoveGeneratorProcess_Exited(object sender, EventArgs e)
    {
    }

    private void MoveGeneratorProcess_ErrorDataReceived(object sender, DataReceivedEventArgs e)
    {
        if(e.Data != null)
        {
            processError.AppendLine(e.Data);
        }
    }

    private void MoveGeneratorProcess_OutputDataReceived(object sender, DataReceivedEventArgs e)
    {
        if (e.Data != null)
        {
            //Console.WriteLine("///// " + e.Data.ToString());
            processOutput.AppendLine(e.Data);
            processOutputLastLine = e.Data;
        }
        else
        {
            int breakme = 0;
        }
    }

    public LinkedList<string> getMoves(string FEN)
    {
        LinkedList<string> movesList = new LinkedList<string>();

        processInput.WriteLine("position fen \"" + FEN + "\"");
        processInput.WriteLine("d");
        processOutput.Clear();
        processInput.WriteLine("go depth 1");

        while (processOutputLastLine.Contains("bestmove") == false && moveGeneratorProcess.HasExited == false)
        {
        }

        if(moveGeneratorProcess.HasExited)
        {
            Init(); // should always be running - exits if FEN is incorrect
            // Throw error???
        }
        else
        {
            // Parse legal/valid moves
            string[] lines = processOutput.ToString().Split(new[] { Environment.NewLine }, StringSplitOptions.None);
            for (int i = 0; i < lines.Length; i++)
            {
                string[] line = lines[i].Split(new[] { " " }, StringSplitOptions.None);
                //if(line[0].Equals("Stockfish"))
                //{
                //    continue;
                //}

                if(line[0].Equals("info"))
                {
                    string newHit = "";

                    int pvIndex = -1;
                    for (int j = line.Length - 2; j >= 0; j--)
                    {
                        if(line[j].Equals("pv"))
                        {
                            pvIndex = j;
                            break;
                        }
                    }

                    if (pvIndex != -1)
                    {
                        newHit = line[pvIndex + 1];
                        movesList.AddLast(ConvertToIdexBasedMove(newHit));
                    }
                }
                else
                {
                    //break;
                    continue;
                }
            }
        }

        //Console.WriteLine(processOutput.ToString());
        //foreach(string move in movesList)
        //{
        //    Console.WriteLine(move);
        //}

        return movesList;
    }

    public char ConvertAlphabetToNumeric(char name)
    {
        if(name.Equals('a'))
        {
            return '1';
        }
        else if (name.Equals('b'))
        {
            return '2';
        }
        else if (name.Equals('c'))
        {
            return '3';
        }
        else if (name.Equals('d'))
        {
            return '4';
        }
        else if (name.Equals('e'))
        {
            return '5';
        }
        else if (name.Equals('f'))
        {
            return '6';
        }
        else if (name.Equals('g'))
        {
            return '7';
        }
        else/*(name.Equals('h'))*/
        {
            return '8';
        }
    }

    public string ConvertToNumberBasedMove(string move)
    {
        return new string(new[] { ConvertAlphabetToNumeric(move[0]), move[1], ConvertAlphabetToNumeric(move[2]), move[3] });
    }

    public string ConvertToIdexBasedMove(string move)
    {
        string rez = ConvertToNumberBasedMove(move);

        int x1 = (int)char.GetNumericValue(rez, 0) - 1;
        int y1 = (int)char.GetNumericValue(rez, 1) - 1;
        int x2 = (int)char.GetNumericValue(rez, 2) - 1;
        int y2 = (int)char.GetNumericValue(rez, 3) - 1;
        x1 = (x1 * -1 + 7);
        //y1 = (y1 * -1 + 7);
        x2 = (x2 * -1 + 7);
        //y2 = (y2 * -1 + 7);

        rez = x1.ToString() + y1.ToString() + x2.ToString() + y2.ToString();

        processOutput.Clear();
        processOutputLastLine = "";

        return rez;
    }
}