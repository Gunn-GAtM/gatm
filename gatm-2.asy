if(!settings.multipleView) settings.batchView=false;
settings.tex="pdflatex";
settings.inlinetex=true;
deletepreamble();
defaultfilename="gatm-2";
if(settings.render < 0) settings.render=4;
settings.outformat="";
settings.inlineimage=true;
settings.embed=true;
settings.toolbar=false;
viewportmargin=(2,2);


int factorial(int n) { // Tail recursion... why not?
if (n == 0 || n == 1)
return 1;
return n * factorial(n - 1);
}

void drawConnect(pair tloffset, int[] mapping = {0}, int cols = 3, real xd = 1, real yd = 1.5) {
int rows = mapping.length + 1;
for (int x = 0; x < cols; ++x) {
for (int y = 0; y < rows; ++y) {
if (y < rows - 1) {
int map = mapping[y];
int[] needs;
int[] truemap;

for (int c = 0; c < cols; ++c) needs.push(c);

for (int i = 0; i < cols; ++i) {
int fact = factorial(cols - i - 1);

int egg = map # fact; // Integer division lolololol
int indx = needs[egg];
needs.delete(egg);

map %= fact;

draw((tloffset + (i * xd, -y * yd)) -- (tloffset + (indx * xd, (-y-1) * yd)));
}
}

dot(tloffset + (x * xd, -y * yd));
}
}
}


size(250);

int[] indices = {0,1,5,2,4,3};
string[] labels = {"I", "A", "B", "C", "D", "E"};

for (int i = 0; i < 6; ++i) {
int[] indx = {indices[i]};
drawConnect((4 * i, 0), indx);
label("$" + labels[i] + "$", (4 * i + 1, -2.5));
}
