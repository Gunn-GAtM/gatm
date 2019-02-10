if(!settings.multipleView) settings.batchView=false;
settings.tex="pdflatex";
settings.inlinetex=true;
deletepreamble();
defaultfilename="cover_source-1";
if(settings.render < 0) settings.render=4;
settings.outformat="";
settings.inlineimage=true;
settings.embed=true;
settings.toolbar=false;
viewportmargin=(2,2);

size(540);

pair cis(real theta) { // Gives points on the unit circle
return (cos(theta), sin(theta));
}


pair A = cis(-pi/6), B = cis(pi/2), C = cis(7*pi/6); // Starting triangle corners

for (int i = 0; i < 4; ++i) { // Draws the triangles and dots
draw(A--B--C--cycle);

dot(A);
dot(B);
dot(C);

if (i < 3) {
A *= -2; B *= -2; C *= -2; // Scales A,B,C to the next triangle
}
}

dot((0,0)); // Center dot

draw(A--(-1/2 * A), dashed);
draw(B--(-1/2 * B), dashed);
draw(C--(-1/2 * C), dashed);


label("{\bfseries \fontsize{36}{48} \selectfont A Geometric Approach to}", -59/128 * B, N); // preferably i wouldn't have this so arbitrary, this -59/128 is to position it perfectly on the triangle.
draw(circle((0,0), 8));
label("{\bfseries \fontsize{84}{112} \selectfont Matrices}", 23/64 * B);
label("{\bfseries \fontsize{18}{24} \selectfont Peter Herreshoff \textit{et al.}}", 11/16 * B);
label("{\bfseries \fontsize{12}{16} \selectfont Gunn High School Analysis H}", 12/16 * B);

