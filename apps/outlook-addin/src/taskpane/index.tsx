import * as React from "react";
import * as ReactDOM from "react-dom";
import TaskPane from "./taskpane";

const container = document.getElementById("root");
if (container) {
  ReactDOM.render(<TaskPane />, container);
}
