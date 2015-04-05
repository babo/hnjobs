var

Comment = React.createClass({
    render: function () {
        var rawMarkup = this.props.children.toString(),
            p = rawMarkup.indexOf('<p>'),
            title = p === -1 ? rawMarkup : rawMarkup.substring(0, p),
            body = p === -1 ? '' : rawMarkup.substring(p);
        return (
            <div className='comment list-group-item'>
                <h4 class="list-group-item" dangerouslySetInnerHTML={{__html: title}}></h4>
                <span dangerouslySetInnerHTML={{__html: body}} />
                <li className='commentAuthor' >
                    {this.props.author}
                </li>
            </div>
        );
    }
}),

CommentList = React.createClass({
    render: function () {
        var commentNodes = this.props.data.map(function (comment) {
            return (
                <Comment author={comment.by}  key={comment.id}>
                    {comment.text}
                </Comment>
            );
        });
        return (
            <div className='commentList list-group'>
                {commentNodes}
            </div>
        );
    }
}),

CommentForm = React.createClass({
    handleSubmit: function (e) {
            e.preventDefault();
            var author = React.findDOMNode(this.refs.author).value.trim(),
                text = React.findDOMNode(this.refs.text).value.trim();

            if (text && author) {
                this.props.onCommentSubmit({
                    author: author,
                    text: text});
                React.findDOMNode(this.refs.author).value = '';
                React.findDOMNode(this.refs.text).value = '';
                React.findDOMNode(this.refs.author).select();
            }
    },
    render: function () {
        return (
            <form className='commentForm' onSubmit={this.handleSubmit}>
                <input type="text" ref="author" placeholder="Your name" />
                <input type="text" ref="text" placeholder="Say something..." />
                <input type="submit" value="POST" />
            </form>
        );
    }
}),

CommentBox = React.createClass({
    loadCommentsFromServer: function () {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            success: function (data) {
                this.setState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        this.loadCommentsFromServer();
        if (this.props.pollInterval !== undefined) {
            setInterval(this.loadCommentsFromServer, this.props.pollInterval);
        }
    },
    handleCommentSubmit: function (comment) {
        var comments = this.state.data,
            newComments = comments.concat([comment]);
        this.setState({data: newComments});
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            type: 'POST',
            data: comment,
            success: function (data) {
                this.setState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    render: function () {
        return (
            <div className='commentBox'>
                <h1>Jobs</h1>
                <CommentList data={this.state.data} />
                <CommentForm onCommentSubmit={this.handleCommentSubmit} />
            </div>
        );
    }
});

React.render(
    <CommentBox url='/hnjobs' pollInterval2={2000}/>,
    document.getElementById('content')
);
