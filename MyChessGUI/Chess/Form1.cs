using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Chess
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private Panel ccMainContainer;
        private Chessboard chessboard1;
        private RichTextBox ccLogging;
        private Button ccTurnBoard;
        private Button ccNewGame;

        private void Form1_Load(object sender, EventArgs e)
        {
            Width = (int)(1200 * 0.75 * 2);
            Height = (int)(900 * 0.75);
            InitComponents();
            ResizeComponents();
        }

        private void InitComponents()
        {
            SizeChanged += Form1_SizeChanged;
            Text = "Simple chess AI by Robert Barachini";

            ccMainContainer = new Panel()
            {
                Dock = DockStyle.Fill,
                Parent = this,
                BackColor = Color.FromArgb(58, 58, 58),
            };
            Controls.Add(ccMainContainer);

            chessboard1 = new Chessboard()
            {
                Parent = ccMainContainer
            };
            chessboard1.PieceMoved += Chessboard1_PieceMoved;
            chessboard1.ScoreImproved += Chessboard1_ScoreImproved;
            ccMainContainer.Controls.Add(chessboard1);

            ccLogging = new RichTextBox()
            {
                Parent = ccMainContainer,
                BackColor = Color.White,
                ForeColor = Color.Black,
                BorderStyle = BorderStyle.None,
                ReadOnly = true
            };
            ccLogging.Font = new Font(new FontFamily("Consolas"), 14);
            ccMainContainer.Controls.Add(ccLogging);

            ccTurnBoard = new Button()
            {
                Parent = ccMainContainer,
                Text = "Turn board",
                FlatStyle = FlatStyle.Flat,
                ForeColor = Color.FromArgb(255, 255, 255),
                BackColor = Color.FromArgb(58, 58, 58),
                Font = new Font(new FontFamily("Segoe UI"), 12)
            };
            ccTurnBoard.Click += CcTurnBoard_Click;
            ccMainContainer.Controls.Add(ccTurnBoard);

            ccNewGame = new Button()
            {
                Parent = ccMainContainer,
                Text = "New game",
                FlatStyle = FlatStyle.Flat,
                ForeColor = Color.FromArgb(255, 255, 255),
                BackColor = Color.FromArgb(58, 58, 58),
                Font = new Font(new FontFamily("Segoe UI"), 12)
            };
            ccNewGame.Click += CcNewGame_Click;
            ccMainContainer.Controls.Add(ccNewGame);
        }

        private void CcNewGame_Click(object sender, EventArgs e)
        {
            chessboard1.SetUpBoard();
        }

        private void Chessboard1_ScoreImproved(Chessboard sender, MiniMaxContext context)
        {
            ccLogging.AppendText("SCORE IMPROVE: <" + context.scoreEval.ToString() + "> -> " + context.piece.ToString() + " to " + context.newLocation.X.ToString() + "," + context.newLocation.Y.ToString() + Environment.NewLine);
            ccLogging.ScrollToCaret();
        }

        private void CcTurnBoard_Click(object sender, EventArgs e)
        {
            chessboard1.facingLight = ! chessboard1.facingLight;
            chessboard1.Invalidate();
        }

        private void Chessboard1_PieceMoved(Chessboard sender)
        {
            ccLogging.AppendText("(" + sender.piecesLight.Count + ") ");
            foreach(ChessPiece c in sender.piecesLight)
            {
                ccLogging.AppendText("[" + sender.ChessPiecePositionToString(c.Xindex, c.Yindex).Replace(" ", "") + " " + c.pieceType.ToString() + "], ");
            }
            ccLogging.AppendText(Environment.NewLine + Environment.NewLine);
            ccLogging.AppendText("(" + sender.piecesDark.Count + ") ");
            foreach (ChessPiece c in sender.piecesDark)
            {
                ccLogging.AppendText("[" + sender.ChessPiecePositionToString(c.Xindex, c.Yindex).Replace(" ", "") + " " + c.pieceType.ToString() + "], ");
            }
            ccLogging.AppendText(Environment.NewLine + Environment.NewLine);
            ccLogging.AppendText(sender.BoardToString());
            ccLogging.AppendText(Environment.NewLine);
            ccLogging.AppendText("Nodes: " + sender.nodesCount + Environment.NewLine);
            ccLogging.AppendText("Moves: " + sender.movesCount + Environment.NewLine);
            ccLogging.AppendText("Elapsed seconds: " + (sender.elapsedTime / 1000).ToString());
            if(sender.IsLightTurn())
            {
                ccLogging.AppendText(Environment.NewLine + "LIGHT TURN");
            }
            else
            {
                ccLogging.AppendText(Environment.NewLine + "DARK TURN");
            }
            ccLogging.AppendText(Environment.NewLine + "----------------------------");
            ccLogging.AppendText(Environment.NewLine + Environment.NewLine);

            ccLogging.ScrollToCaret();
        }

        private void Form1_SizeChanged(object sender, EventArgs e)
        {
            try
            {
                ResizeComponents();
            }
            catch(Exception ex) { }
        }

        private void ResizeComponents()
        {
            SuspendLayout();

            chessboard1.Top = 50;
            chessboard1.Left = 50;
            chessboard1.Height = (int)(ccMainContainer.Height * 0.8);
            chessboard1.Width = chessboard1.Height; //(int)(ccMainContainer.Width * 0.8);
            chessboard1.Invalidate();

            ccLogging.Top = chessboard1.Top;
            ccLogging.Left = chessboard1.Left + chessboard1.Width + 30;
            ccLogging.Height = chessboard1.Height;
            ccLogging.Width = ccLogging.Parent.Width - chessboard1.Width - chessboard1.Left - 60;

            ccTurnBoard.Left = chessboard1.Left;
            ccTurnBoard.Top = 10;
            ccTurnBoard.Height = 32;
            ccTurnBoard.Width = 120;

            ccNewGame.Left = ccTurnBoard.Left + ccTurnBoard.Width + 15;
            ccNewGame.Top = ccTurnBoard.Top;
            ccNewGame.Height = ccTurnBoard.Height;
            ccNewGame.Width = 120;

            ResumeLayout();
        }
    }
}
