using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Chess
{
    public class MiniMaxContext
    {
        public double scoreEval;
        public ChessPiece piece;
        public Point newLocation;
        public double alpha;
        public double beta;

        public MiniMaxContext()
        {
            this.scoreEval = double.MinValue;
            this.alpha = double.MinValue;
            this.beta = double.MaxValue;
        }
    }
}
